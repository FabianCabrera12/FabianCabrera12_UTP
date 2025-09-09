# Proyecto_lab/_SRC/main.py
# ============================================================
# Limpieza de CSV/TXT de voltajes, conversión a °C (T=18*V-64),
# alertas (>40°C) y KPIs, con la estructura:
#   Proyecto_lab/
#     _SRC/               (este archivo y diagrama_de_flujo.txt)
#     _DATA/
#       _RAW/             (entrada sucia: datos_sucios_250_v2.csv)
#       _PROCESSED/       (salidas: Temperaturas_Procesado.csv, KPIs.json)
# ============================================================

import csv
import json
import statistics
from datetime import datetime
from pathlib import Path
import argparse
from typing import Dict, List, Any

# ------------ Configuración / limpieza ------------
BAD_STRINGS = {"", "na", "n/a", "nan", "null", "none", "error", "err", "nulo"}

TS_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M",
]

# ------------ Helpers ------------
def normalize_decimal(s: str) -> str:
    """Reemplaza coma por punto y quita espacios."""
    return (s or "").replace(",", ".").strip()

def is_bad_value(s: str) -> bool:
    return (s or "").lower().strip() in BAD_STRINGS

def parse_float(s: str) -> float:
    """Convierte a float (lanza ValueError si es inválido)."""
    s = normalize_decimal(s).replace(" ", "")
    if is_bad_value(s):
        raise ValueError("valor inválido")
    return float(s)

def parse_timestamp(s: str) -> datetime:
    """Intenta múltiples formatos y normaliza a datetime."""
    raw = (s or "").strip()
    if is_bad_value(raw):
        raise ValueError("timestamp inválido")
    for fmt in TS_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass
    # Manejo simple si viniera con milisegundos (descarta la parte .xxx)
    if "." in raw:
        base = raw.split(".", 1)[0].rstrip("Z")
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(base, fmt)
            except ValueError:
                pass
    raise ValueError(f"timestamp no reconocido: {raw}")

def volt_to_temp(v: float) -> float:
    """Relación del sensor pedida: T(°C) = 18*V - 64."""
    return 18.0 * v - 64.0

def format_ts(dt: datetime) -> str:
    """Formato estándar de salida."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def detectar_delimitador(path: Path, default=";") -> str:
    """Heurística simple para detectar ';' o ',' en cabecera."""
    try:
        with path.open("r", encoding="utf-8") as f:
            head = f.readline()
        return ";" if head.count(";") >= head.count(",") else ","
    except Exception:
        return default

# ------------ Núcleo ------------
def procesar_csv(in_path: Path, out_path: Path) -> Dict[str, Any]:
    """
    Lee, limpia y escribe el CSV procesado con cabeceras:
    Timestamp;Voltaje;Temp_C;Alertas
    Devuelve KPIs.
    """
    stats = {
        "Filas_totales": 0,
        "Filas_validas": 0,
        "Descartes_Timestamp": 0,
        "Descartes_valor": 0,
        "Alertas": 0,
        "n": 0,
        "temp_min": None,
        "temp_max": None,
        "temp_prom": None,
    }
    temps: List[float] = []

    delim_in = detectar_delimitador(in_path, default=";")

    with in_path.open("r", encoding="utf-8", newline="") as f_in, \
         out_path.open("w", encoding="utf-8", newline="") as f_out:

        reader = csv.DictReader(f_in, delimiter=delim_in)
        writer = csv.DictWriter(
            f_out,
            fieldnames=["Timestamp", "Voltaje", "Temp_C", "Alertas"],
            delimiter=";",
        )
        writer.writeheader()

        for row in reader:
            stats["Filas_totales"] += 1

            ts_raw = (row.get("timestamp") or row.get("Timestamp") or "").strip()
            v_raw  = (row.get("value") or row.get("Voltaje") or row.get("voltage") or "").strip()

            # Valor
            try:
                v = parse_float(v_raw)
            except Exception:
                stats["Descartes_valor"] += 1
                continue

            # Timestamp
            try:
                ts = parse_timestamp(ts_raw)
            except Exception:
                stats["Descartes_Timestamp"] += 1
                continue

            # Temperatura y alerta
            t = round(volt_to_temp(v), 2)
            alerta = "ALERTA" if t > 40.0 else "OK"
            if alerta == "ALERTA":
                stats["Alertas"] += 1

            writer.writerow({
                "Timestamp": format_ts(ts),
                "Voltaje": f"{v:.3f}",
                "Temp_C": f"{t:.2f}",
                "Alertas": alerta
            })

            stats["Filas_validas"] += 1
            temps.append(t)

    if temps:
        stats["n"] = len(temps)
        stats["temp_min"] = min(temps)
        stats["temp_max"] = max(temps)
        stats["temp_prom"] = round(statistics.fmean(temps), 2)

    return stats

def guardar_kpis(kpis: Dict[str, Any], kpi_path: Path) -> None:
    kpi_path.write_text(json.dumps(kpis, ensure_ascii=False, indent=2), encoding="utf-8")

def guardar_diagrama_flujo(path: Path) -> None:
    texto = """
[INICIO]
  |
  v
[Leer archivo _DATA/_RAW con csv.DictReader]
  |
  v
[Por cada fila]
  |
  +--> 'value' → float (comas→puntos; NA/error ⇒ Descarte_valor)
  +--> 'timestamp' → datetime (múltiples formatos; si falla ⇒ Descarte_timestamp)
  +--> Temp = 18*V - 64  (2 decimales)
  +--> Alert = Temp>40 ? 'ALERTA' : 'OK'
  +--> Escribir → _DATA/_PROCESSED/Temperaturas_Procesado.csv (;) con cabeceras
  +--> Acumular KPIs (min, max, prom, contadores)
[Fin] → Guardar _DATA/_PROCESSED/KPIs.json
""".strip("\n")
    path.write_text(texto, encoding="utf-8")

# ------------ CLI / main ------------
def main():
    base = Path(__file__).resolve().parents[1]  # Proyecto_lab/
    raw_default = base / "_DATA" / "_RAW" / "datos_sucios_250_v2.csv"

    parser = argparse.ArgumentParser(
        description="Limpia datos_sucios_250_v2.* en _DATA/_RAW, convierte a °C, etiqueta alertas (>40°C) y genera salidas en _DATA/_PROCESSED."
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        type=str,
        default=str(raw_default),
        help="Ruta del archivo de entrada (.csv/.txt). Default: _DATA/_RAW/datos_sucios_250_v2.csv",
    )
    args = parser.parse_args()

    in_path = Path(args.in_path)
    out_dir  = base / "_DATA" / "_PROCESSED"
    docs_dir = base / "_SRC"
    out_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Fallback si no existe el default
    if not in_path.exists():
        cand1 = base / "_DATA" / "_RAW" / "datos_sucios_250_v2.csv"
        cand2 = base / "_DATA" / "_RAW" / "datos_sucios_250_v2.txt"
        if cand1.exists(): in_path = cand1
        elif cand2.exists(): in_path = cand2

    out_csv = out_dir / "Temperaturas_Procesado.csv"
    out_kpi = out_dir / "KPIs.json"
    flow    = docs_dir / "diagrama_de_flujo.txt"

    if not in_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de entrada:\n  {in_path}\n"
            f"Colócalo en: {raw_default} o pásalo con --in RUTA/AL/ARCHIVO.csv|.txt"
        )

    kpis = procesar_csv(in_path, out_csv)
    guardar_kpis(kpis, out_kpi)
    guardar_diagrama_flujo(flow)

    print("\n=== KPIs ===")
    print(json.dumps(kpis, ensure_ascii=False, indent=2))
    print("\nArchivos generados:")
    print(f"- {out_csv}")
    print(f"- {out_kpi}")
    print(f"- {flow}")

if __name__ == "__main__":
    main()


