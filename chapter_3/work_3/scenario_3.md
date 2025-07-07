# Reporte de Implementación de Pipeline de Datos para Local Pipeline

En este documento se detalla la implementación de un pipeline de procesamiento de datos por lotes orquestado para las compañías DataDriven y LeadData. El pipeline está diseñado para ejecutarse diariamente, haciendo que los datos estén disponibles a las 08:00 AM, cubriendo la extracción a la capa Bronze, la transformación a la capa Silver y la carga a la capa Golden, con tablas específicas para consumo analítico y seguridad de datos.

---

## Configuración del Entorno Docker

Se estableció  un entorno de desarrollo local conteneurizado utilizando Docker y Docker Compose para alojar Apache Airflow y PostgreSQL, permitiendo la orquestación del pipeline.


1. **Preparación del Entorno:**

   - Verificación de la correcta instalación de Docker Desktop.
   - Descarga y modificación de docker-compose.yml (construcción de imagen personalizada, LOAD_EXAMPLES=false, montajes de dbt y data, exposición de puerto 5433:5432).
   - Creación de requirements.txt (dbt-core, dbt-postgres, faker, polars).
   - Creación de Dockerfile (basado en apache/airflow:2.10.2, copia e instalación de requirements.txt, copia de directorio dbt).

### Evidencia (Capturas de Pantalla)

- [ ] **Captura de pantalla de localización de archivos en work_3** (Ver archivo `1.png` en el directorio `work_3/screenshots/`.)

---

2. **Configuración e Implementación de dbt.**

  - Estructura del Proyecto dbt: Creación de directorios dbt y dbt/models.
  - Archivos de Configuración dbt: dbt_project.yml: Configuración del proyecto (dbt_driven_data, perfil default, model-paths)
  - profiles.yml: Conexión PostgreSQL (host: postgres, user: airflow, dbname: airflow, schema: driven)
  - source.yml: Definición de fuentes (raw_source, staging_source, trusted_source)

  - Creación de Modelos dbt:
        - Modelos Staging (dbt/models/staging_*.sql): dim_address, dim_date, dim_finance, dim_person, fact_network_usage. Transformaciones básicas de raw_batch_data.
        
        - Modelos Trusted (dbt/models/trusted_*.sql): payment_data, technical_data, non_pii_data (enmascarado), pii_data (sin enmascarar). Lógica de negocio y JOINs desde staging.

### Evidencia (Capturas de Pantalla)

- [ ] **Captura de pantalla de estructura de archivos en work_3** (Ver archivo `2.png` en el directorio `work_3/screenshots/`.)
- [ ] **Captura de pantalla los modelos en directorio** (Ver archivo `3.png` en el directorio `work_3/screenshots/`.)

---

3. **Orquestación con Apache Airflow**

   - Ejecución de Contenedores:bComando docker-compose up --build.
   - Verificación en Docker Desktop (contenedores, imágenes, volumen).
   - Acceso a Airflow UI: Acceso a http://localhost:8080 y login (airflow/airflow).
   - Configuración de Conexión: Creación de conexión postgres_conn (Tipo: PostgreSQL, Host: postgres, Puerto: 5432, DB: airflow, User: airflow, Pass: airflow).
   - Creación del DAG (driven_data_pipeline.py): Archivo work_3/dags/driven_data_pipeline.py.
   - DAG: extract_raw_data_pipeline (diario a las 07:00 AM).
   - Tareas: extract_raw_data_task (Python), create_raw_schema_task (SQL), create_raw_table_task (SQL), load_raw_data_task (SQL COPY), run_dbt_staging_task (Bash, dbt run --select tag:staging), run_dbt_trusted_task (Bash, dbt run --select tag:trusted).
   - Dependencias: [extract_raw_data_task, create_raw_schema_task] >> create_raw_table_task >> load_raw_data_task >> run_dbt_staging_task >> run_dbt_trusted_task.

### Evidencia (Capturas de Pantalla)

- [ ] **Captura de pantalla de volumenes Docker activos** (Ver archivo `4.png` en el directorio `work_3/screenshots/`.)
- [ ] **Captura de pantalla de imagenes Docker activas** (Ver archivo `5.png` en el directorio `work_3/screenshots/`.)
- [ ] **Captura de pantalla de contenedores Docker activos** (Ver archivo `6.png` en el directorio `work_3/screenshots/`.)
- [ ] **Captura de pantalla del DAG en funcionamiento.** (Ver archivo `7.png` en el directorio `work_3/screenshots/`.)
- [ ] **Captura de pantalla de la gráfica del DAG en funcionamiento** (Ver archivo `8.png` en el directorio `work_3/screenshots/`.)

---

4. **Ejecución del Pipeline y Verificación de Datos.**

  - Ejecución del DAG: Activación y ejecución del DAG en Airflow UIy el monitoreo de tareas y revisión de logs (especialmente dbt tags).
  - Verificación en pgAdmin 4: Conexión al servidor airflow (localhost:5433, DB: airflow, User: airflow, Pass: airflow). Exploración de esquemas (driven_raw, driven_staging, driven_trusted) y tablas.
  - Confirmar datos con la setencia SELECT unique_id, iban, download_speed, upload_speed, session_duration, consumed_traffic, payment_amount
    FROM driven_trusted.payment_data
        WHERE download_speed > 750;

### Evidencia (Capturas de Pantalla)

- [ ] **Captura de la creación del server airflow con la conexión de la BD** (Ver archivo `9.png` en el directorio `work_3/screenshots/`.)
- [ ] **Captura del resultado del QUERY** (Ver archivo `10.png` en el directorio `work_3/screenshots/`.)

---

## Conclusiones

A través de esta práctica pude comprender y aplicar los principios fundamentales del procesamiento de datos por lotes en un entorno local.  También aprendi a construir un pipeline orquestado con Apache Airflow, contenedorizado con Docker y respaldado por PostgreSQL, integrando herramientas como dbt para modelado de datos y Faker para generar datos sintéticos. Además, reforcé buenas prácticas de organización de proyectos, configuración de conexiones, monitoreo de flujos y verificación de datos mediante pgAdmin.
Todo esto me permitió visualizar de forma clara cómo se estructura y automatiza un flujo de procesamiento de datos en etapas (raw, staging, trusted) para su posterior análisis.