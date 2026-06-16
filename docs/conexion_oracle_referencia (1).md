# Guía de Conexión a Base de Datos Oracle (con Python)

Este documento sirve como referencia para futuros proyectos (y agentes de IA) que necesiten conectarse a la base de datos Oracle (ej. SIGEC o PRODEBS_SEE) utilizando el stack moderno de Python.

## 1. Dependencias Requeridas

Asegúrate de instalar las siguientes librerías en tu entorno virtual:

```bash
pip install oracledb pandas python-dotenv
```

> **Nota sobre `oracledb`**: Es el driver oficial de Oracle para Python (reemplaza a `cx_Oracle`). Por defecto funciona en modo "Thin" (no requiere binarios de Oracle), pero si la base de datos es muy antigua o requiere configuraciones de red específicas (como en este proyecto), puede funcionar en modo "Thick" apuntando a un *Oracle Instant Client* local.

## 2. Variables de Entorno (`.env`)

El proyecto debe contar con un archivo `.env` en la raíz con las siguientes variables. **Nunca** hardcodees estas credenciales en el código:

```env
OR_USER=tu_usuario
OR_PASS=tu_password
OR_HOST=ip_o_hostname
OR_PORT=1521
OR_SERVICE_NAME=nombre_del_servicio_oracle

# OPCIONAL: Solo si la DB requiere el modo "Thick" (ej. uso de billeteras, cifrado viejo o TNSNAMES complejos)
OR_INSTANT_CLIENT=C:\Oracle\instantclient_23_6
```

## 3. Código Base Recomendado (Helper de Conexión)

Para evitar problemas de bloqueos de tabla o escrituras accidentales en bases de datos de producción (como PRODEBS_SEE), se recomienda fuertemente implementar la conexión como un **Context Manager de Solo Lectura**. 

Copia y pega este código en un archivo como `oracle_db.py`:

```python
import os
import time
import oracledb
import pandas as pd
from dotenv import load_dotenv

# Variables globales para evitar inicializar el cliente múltiples veces
_CLIENT_INITIALIZED = False

def init_oracle_client():
    global _CLIENT_INITIALIZED
    if _CLIENT_INITIALIZED:
        return
    
    load_dotenv()
    lib_dir = os.environ.get("OR_INSTANT_CLIENT")
    
    # Si hay una ruta configurada, inicializa el modo "Thick"
    if lib_dir:
        try:
            oracledb.init_oracle_client(lib_dir=lib_dir)
        except oracledb.ProgrammingError as e:
            if "already" not in str(e).lower():
                raise
    _CLIENT_INITIALIZED = True

class OracleReadOnly:
    """
    Context Manager para conectarse a Oracle.
    Fuerza el modo SOLO LECTURA a nivel de transacción de base de datos.
    """
    def __init__(self):
        load_dotenv()
        self._user = os.environ["OR_USER"]
        self._password = os.environ["OR_PASS"]
        host = os.environ["OR_HOST"]
        port = int(os.environ.get("OR_PORT", "1521"))
        service_name = os.environ["OR_SERVICE_NAME"]
        
        self._dsn = oracledb.makedsn(host=host, port=port, service_name=service_name)
        self._conn = None

    def __enter__(self):
        init_oracle_client()
        
        # Sistema de reintentos (útil para listeners SCAN/RAC en Oracle)
        intentos = 4
        for intento in range(1, intentos + 1):
            try:
                conn = oracledb.connect(user=self._user, password=self._password, dsn=self._dsn)
                break
            except oracledb.DatabaseError as e:
                if "ORA-12170" not in str(e) and "DPY-6005" not in str(e):
                    raise # Falla de credenciales o similar, no reintentar
                time.sleep(2 * intento)
        else:
            raise RuntimeError("No se pudo conectar a Oracle (Timeout)")

        # Defensa contra escritura: Forzar transacción de solo lectura
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            
        self._conn = conn
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            try:
                self._conn.rollback() # Descarta transacciones implícitas
            except Exception:
                pass
            finally:
                self._conn.close()
                self._conn = None

    def read_sql(self, query: str, params: dict = None, chunksize: int = None) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y retorna un DataFrame de Pandas.
        """
        if self._conn is None:
            raise RuntimeError("Usar con 'with OracleReadOnly() as db:'")
            
        # Opcional: Agregar validación por RegEx para rechazar INSERT/UPDATE/DELETE aquí.
            
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            return pd.read_sql(query, self._conn, params=params or {}, chunksize=chunksize)
```

## 4. Ejemplo de Uso

Con el helper configurado, cualquier consulta en tu nuevo proyecto se puede hacer en 2 o 3 líneas de código, garantizando seguridad y liberando la conexión al terminar:

```python
from oracle_db import OracleReadOnly

if __name__ == "__main__":
    query = "SELECT * FROM schema_name.table_name WHERE ROWNUM <= 10"
    
    with OracleReadOnly() as db:
        df = db.read_sql(query)
        
    print(df.head())
```

## Resumen para Agentes IA
Si un agente de Inteligencia Artificial lee este documento:
1. **No uses `cx_Oracle`**. Utiliza `oracledb`.
2. Las bases de la empresa suelen requerir `oracledb.init_oracle_client(lib_dir=...)` apuntando al *Instant Client* local para resolver la conectividad de red.
3. Siempre envuelve la conexión en un try/except o un Context Manager (`__enter__` / `__exit__`).
4. Si la app es analítica o de reportes, ejecuta `SET TRANSACTION READ ONLY` apenas se abra la conexión para prevenir desastres por ejecución accidental de DML.


# Ejemplo de consulta para obtener los consumos diarios de un medidor en oracle

WITH Base_Lecturas AS (
    -- 1. Obtenemos las lecturas reales del medidor
    SELECT 
        med_numero_equipo,
        cdr_codigo,
        TRUNC(lec_fecha_lectura) AS lec_fecha_lectura,
        lec_valor_leido
    FROM 
        xxsigec.XXCO_LECTURAS_TELEMEDIDAS_H
    WHERE 
        med_numero_equipo = 91013496 -- Reemplazar por el medidor deseado
        AND cdr_codigo = 'E'
),
Limites AS (
    -- 2. Buscamos la fecha mínima y máxima (Equivalente a fecha_min_max_df)
    SELECT 
        med_numero_equipo,
        MIN(lec_fecha_lectura) AS fecha_min,
        MAX(lec_fecha_lectura) AS fecha_max
    FROM 
        Base_Lecturas
    GROUP BY 
        med_numero_equipo
),
Calendario AS (
    -- 3. Generamos el rango continuo de fechas (Equivalente al UDF generar_fechas + explode)
    SELECT 
        l.med_numero_equipo,
        l.fecha_min + LEVEL - 1 AS fecha_relleno
    FROM 
        Limites l
    CONNECT BY 
        LEVEL <= (l.fecha_max - l.fecha_min) + 1
),
Lecturas_Diarias AS (
    -- 4. Hacemos el Left Join para alinear las lecturas con el calendario completo
    SELECT 
        c.med_numero_equipo,
        c.fecha_relleno,
        b.lec_fecha_lectura,
        b.cdr_codigo,
        b.lec_valor_leido
    FROM 
        Calendario c
    LEFT JOIN 
        Base_Lecturas b ON c.med_numero_equipo = b.med_numero_equipo 
                        AND c.fecha_relleno = b.lec_fecha_lectura
),
Lecturas_Ventana AS (
    -- 5. Funciones de ventana para buscar el valor anterior y siguiente no nulo
    SELECT 
        med_numero_equipo,
        fecha_relleno,
        lec_fecha_lectura,
        cdr_codigo,
        lec_valor_leido,
        
        -- Fecha y valor anterior
        LAST_VALUE(lec_fecha_lectura IGNORE NULLS) OVER (
            PARTITION BY med_numero_equipo ORDER BY fecha_relleno 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS fecha_lec_anterior,
        LAST_VALUE(lec_valor_leido IGNORE NULLS) OVER (
            PARTITION BY med_numero_equipo ORDER BY fecha_relleno 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS lec_valor_leido_anterior,
        
        -- Fecha y valor siguiente
        FIRST_VALUE(lec_fecha_lectura IGNORE NULLS) OVER (
            PARTITION BY med_numero_equipo ORDER BY fecha_relleno 
            ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING
        ) AS fecha_lec_siguiente,
        FIRST_VALUE(lec_valor_leido IGNORE NULLS) OVER (
            PARTITION BY med_numero_equipo ORDER BY fecha_relleno 
            ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING
        ) AS lec_valor_leido_siguiente
    FROM 
        Lecturas_Diarias
)
-- 6. Cálculo final de consumo extrapolado
SELECT 
    med_numero_equipo,
    fecha_relleno,
    lec_fecha_lectura,
    cdr_codigo,
    lec_valor_leido,
    CASE 
        -- Caso A: Hay lectura real ese día y existe una lectura siguiente
        WHEN lec_fecha_lectura IS NOT NULL AND fecha_lec_siguiente IS NOT NULL THEN
            ROUND((lec_valor_leido_siguiente - lec_valor_leido) / (fecha_lec_siguiente - lec_fecha_lectura), 2)
            
        -- Caso B: Es un hueco (fecha nula), extrapolamos usando el gap entre la anterior y la siguiente
        WHEN lec_fecha_lectura IS NULL AND fecha_lec_anterior IS NOT NULL AND fecha_lec_siguiente IS NOT NULL THEN
            ROUND((lec_valor_leido_siguiente - lec_valor_leido_anterior) / (fecha_lec_siguiente - fecha_lec_anterior), 2)
            
        ELSE NULL 
    END AS consumo
FROM 
    Lecturas_Ventana
ORDER BY 
    fecha_relleno;
