"""Spike N — Extrae datos de cliente para armar el seeder.

Consulta VM_INTELIGENTES para 15 medidores CLOU del listado y
los imprime en formato Python listo para pegar en seed_demo.py.

Uso:
    uv run python -u scripts/spike_cliente_seeder.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_root = Path(__file__).parent.parent
_env_path = _root / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

sys.path.insert(0, str(_root / "src"))
sys.stdout.reconfigure(line_buffering=True)

import oracledb

_REQUIRED = ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME")

# Muestra amplia de medidores CLOU del listado (mix de prefijos)
MUESTRA_CLOU = [
    "90008989",
    "90008245",
    "90008983",
    "90008578",
    "90008384",
    "90010533",
    "90010534",
    "70096469",
    "70096451",
    "70096527",
    "70085039",
    "70084821",
    "70099630",
    "70096463",
    "70096530",
]


def _conectar() -> oracledb.Connection:
    missing = [v for v in _REQUIRED if not os.environ.get(v)]
    if missing:
        print(f"[spike] Faltan variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    instant_client = os.environ.get("OR_INSTANT_CLIENT", "")
    if instant_client and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(instant_client)
    if instant_client:
        try:
            oracledb.init_oracle_client(lib_dir=instant_client)
        except oracledb.ProgrammingError as exc:
            if "already" not in str(exc).lower():
                raise

    dsn = oracledb.makedsn(
        host=os.environ["OR_HOST"],
        port=int(os.environ.get("OR_PORT", "1521")),
        service_name=os.environ["OR_SERVICE_NAME"],
    )
    conn = oracledb.connect(
        user=os.environ["OR_USER"],
        password=os.environ["OR_PASS"],
        dsn=dsn,
    )
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
    return conn


def main() -> None:
    print("# ===== DATOS ORACLE PARA SEED_DEMO.PY =====")
    print("# Generado con spike_cliente_seeder.py\n")

    conn = _conectar()

    try:
        with conn.cursor() as cur:
            ph = ", ".join(f":m{i}" for i in range(len(MUESTRA_CLOU)))
            params = {f"m{i}": v for i, v in enumerate(MUESTRA_CLOU)}

            cur.execute(
                f"""
                SELECT
                    medidor,
                    suministro,
                    razon_social,
                    tipo_documento,
                    nro_documento,
                    cuit,
                    calle,
                    altura,
                    piso,
                    depto,
                    barrio,
                    localidad,
                    datos_adicionales_domicilio,
                    dc_latitud,
                    dc_longitud,
                    codigo_tarifa,
                    grupo_tarifario,
                    telemedible
                FROM GEOREF.VM_INTELIGENTES
                WHERE medidor IN ({ph})
                ORDER BY medidor
            """,
                params,
            )

            rows = cur.fetchall()
            cols = [d[0].lower() for d in cur.description]

            print(f"# {len(rows)} medidores encontrados\n")
            print("CLIENTES_ORACLE = [")
            for row in rows:
                d = dict(zip(cols, row, strict=False))
                srv = str(d["suministro"])
                med = str(d["medidor"])
                nombre = (d["razon_social"] or "").strip().title()
                tipo_doc = d["tipo_documento"] or ""
                nro_doc = d["nro_documento"]
                cuit = d["cuit"]
                calle = (d["calle"] or "").strip().title()
                altura = d["altura"]
                piso = d["piso"]
                depto = d["depto"]
                barrio = (d["barrio"] or "").strip().title()
                localidad = (d["localidad"] or "").strip().title()
                datos_dom = (d["datos_adicionales_domicilio"] or "").strip()
                lat = d["dc_latitud"]
                lon = d["dc_longitud"]
                tarifa = d["codigo_tarifa"]
                grupo = d["grupo_tarifario"]
                telemedible = d["telemedible"]

                # Armar domicilio legible
                domicilio_parts = [f"{calle} {altura}" if altura else calle]
                if piso:
                    domicilio_parts.append(f"Piso {piso}")
                if depto:
                    domicilio_parts.append(f"Dpto {depto}")
                if barrio:
                    domicilio_parts.append(barrio)
                domicilio_parts.append(localidad)
                domicilio = ", ".join(p for p in domicilio_parts if p)

                # username = nro_documento o cuit
                if nro_doc:
                    usuario = str(int(nro_doc))
                elif cuit:
                    usuario = str(int(cuit))
                else:
                    usuario = f"SRV{srv}"

                email = f"{usuario}@plataforma.epec.com.ar"

                print(f"    {{")
                print(f'        "medidor":    "{med}",')
                print(f'        "suministro": "{srv}",')
                print(f'        "nombre":     "{nombre}",')
                print(f'        "tipo_doc":   "{tipo_doc}",')
                print(f'        "nro_doc":    "{int(nro_doc) if nro_doc else ""}",')
                print(f'        "cuit":       "{int(cuit) if cuit else ""}",')
                print(f'        "domicilio":  "{domicilio}",')
                print(f'        "lat":        {lat},')
                print(f'        "lon":        {lon},')
                print(f'        "tarifa":     "{tarifa}",')
                print(f'        "grupo_tar":  "{grupo}",')
                print(f'        "telemedible":"{telemedible}",')
                print(f'        "usuario":    "{usuario}",')
                print(f'        "email":      "{email}",')
                print(f"    }},")
            print("]")

    finally:
        conn.rollback()
        conn.close()


if __name__ == "__main__":
    main()
