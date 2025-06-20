## Scenario 2
For the second chapter/sprint, you need to investigate the data source for *LeadData*, understand the amount of data from the previous months, and identify available fields and data types. Prepare a local ETL pipeline to extract data into the bronze layer (raw zone), apply necessary transformations into the silver layer (staging zone), and upload data to the golden layer (trusted zone) for consumption in the analytical process. It is required that the golden layer contains four tables: a financial table for payment calculations, a technical table for analyzing technical issues, a non-PII table for access by all users with limited access levels across the organization, and a PII table for users with high access levels.

## Instructions 2
Use the directory `chapter_2/work_2/` as your project directory for work related to **Chapter 2** for **LeadData** company.

## Assignment 2
a. Investigate data source.\
b. Extract data:
* i. Data generator.
* ii. Data extraction.

c. Transform data:
* i. Bronze layer.
* ii. Silver layer.

d. Load data:
* i. Financial Data.
* ii. Support Data.
* iii. Non-PII Data.
* iv. PII Data.


--------------------------------------------------------------------------------------------

# Reporte de practica hecho por Montserrat Ruiz Estrada

En este reporte se detallará sobre la implementación de un pipeline de procesamiento de datos por lotes para la empresa LeadData, cubriendo las fases de Extracción, Transformación y Carga (ETL) para generar datos históricos y estructurarlos en un esquema de Data Warehouse.


## 1. Extracción de Datos (Capa Bronze)

### Procedimiento: 

1.  **Configuración del entorno Python:**
    - Se hizo la instalación de las librerías `Faker` y `Polars` usando el comando en terminal `pip install Faker polars`.
    - Después se hizo la configuración del logging para el monitoreo del script.

2.  **Desarrollo del archivo `batch_generator.py`:**
    - Se crearon funciones para:
        - `create_data(locale)`: Esto logra instanciar el generador de datos con la localización rumana requerida (`ro_RO`).
        - `generate_record(fake)`: Esto genera un único registro de usuario con todos los campos definidos.
        - `write_to_csv(file_path, rows)`: Con esta función puedes generar y crear múltiples registros en un archivo CSV. Esta se configuró para generar **100,373 registros** para la carga inicial e histórica.
        - `add_id(file_name)`: Esto añadió una columna `unique_id` (UUID) a cada registro utilizando la librería Polars.
        - `update_datetime(file_name, run)`: Y con esta se actualiza la columna `accessed_at` para simular fechas históricas (para la primera carga) o del día anterior (para otras cargas).

3.  **Lógica de Ejecución (`if __name__ == "__main__":`):**
    - Se implementó esta lógica para diferenciar entre la "primera ejecución" con la "segunda ejecución".
    - El script generó un archivo CSV con la fecha actual en el directorio `work_2/data_2`.

### Evidencia (Capturas de Pantalla / Salida de Consola)
- **Captura de pantalla de la ejecución de `python batch_generator.py` mostrando los logs de inicio y fin.** (Ver archivo `1.png` en el directorio `work_2/screenshots/`.)
- [ ] **Captura de pantalla del archivo CSV generado en `work_2/data_2` en VS Code** (Ver archivo `2.png` en el directorio `work_2/screenshots/`.)

---

## 2. Transformación de Datos (Capa Silver y Golden)


### Procedimiento

#### 2.1. Configuración de PostgreSQL y pgAdmin 4

1.  **Creación de Servidor:** Se creó el servidor `DataDriven` en pgAdmin 4, conectando a `localhost:5432` con el usuario `postgres`.
2.  **Creación de Base de Datos:** Se creó la base de datos `datadriven_db`.
3.  **Creación de Esquemas:** Se crearon los esquemas `bronze_layer`, `silver_layer`, y `golden_layer` para organizar las capas de datos.
4.  **Carga a `bronze_layer`:**
    - Se creó la tabla `bronze_layer.batch_first_load` con todas las columnas y tipos de datos necesarios.
    - Se utilizó el comando `COPY` en el Query Tool para cargar los **100,373 registros** del archivo CSV a esta tabla. Se tuvo que resolver un problema de permisos debido a la ubicación del archivo CSV, por lo que este problema se resolvió moviendo el CSV a una ubicación accesible que en este caso fue creando una nueva carpeta en root (`C:/temp_data`).

#### 2.2. Verificación de Calidad de Datos (Capa Bronze)

1.  **Valores Faltantes:** Se ejecutó la consulta `check_missing_values`. El resultado fue `0`, confirmando la ausencia de valores nulos en el dataset.
2.  **Valores Duplicados:** Se ejecutó la consulta `check_duplicate_values`. No se encontraron filas duplicadas, lo que verifica la unicidad de los registros.

#### 2.3. Modelado de Datos (Capa Silver - Esquema en Estrella)

Se implementó un esquema estrella para desnormalizar la tabla `batch_first_load` en una tabla de hechos y cuatro tablas dimensionales en la `silver_layer`. La organización del esquema fue la siguiente:
-   **`silver_layer.dim_address`**: `unique_id`, `address`, `mac_address`, `ip_address`.
-   **`silver_layer.dim_date`**: `unique_id`, `accessed_at`.
-   **`silver_layer.dim_finance`**: `unique_id`, `iban`.
-   **`silver_layer.dim_person`**: `unique_id`, `person_name`, `user_name`, `email`, `phone`, `birth_date`, `personal_number`.
-   **`silver_layer.fact_network_usage`**: `unique_id`, `session_duration`, `download_speed`, `upload_speed`, `consumed_traffic`.

#### 2.4. Carga y Desnormalización (Capa Golden)

Se crearon tablas específicas para distintos departamentos y casos de uso, combinando y transformando datos de la capa Silver.

1.  **`golden_layer.payment_data` (Para el Departamento Financiero):**
    - Se creó la tabla uniendo `fact_network_usage` y `dim_finance`.
    - Se calculó la columna `payment_amount` utilizando la fórmula `((download_speed + upload_speed + 1)/2) + (consumed_traffic / (session_duration + 1))`.
2.  **`golden_layer.technical_data` (Para el Departamento de Soporte Técnico):**
    - Se creó la tabla uniendo `fact_network_usage` y `dim_address`.
    - Se agregó `min_session_duration` (duración de la sesión en minutos).
    - Se calculó la columna booleana `technical_issue` (true si `download_speed < 50` O `upload_speed < 30` O `session_duration/60 < 1`).
3.  **`golden_layer.non_pii_data` (Datos No PII - Para uso futuro):**
    - Se creó una tabla desnormalizada uniendo todas las dimensiones y la tabla de hechos.
    - Se enmascararon u ofuscaron las columnas con Información Personal Identificable (PII) como `person_name`, `email`, `personal_number`, `address`, `phone`, etc., usando `'***MASKED***'` o `SUBSTRING`.
4.  **`golden_layer.pii_data` (Datos PII - Para uso futuro):**
    - Se creó una tabla desnormalizada uniendo todas las dimensiones y la tabla de hechos.
    - Esta tabla contiene todas las columnas sin enmascarar, destinada a acceso restringido.

### Evidencia (Capturas de Pantalla)
- **Captura de pantalla de pgAdmin 4 mostrando los tres esquemas (`bronze_layer`, `silver_layer`, `golden_layer`).** (Ver archivo `3.png` en el directorio `work_2/screenshots/`.)
- **Captura de pantalla de `bronze_layer.batch_first_load` con `View/Edit Data` mostrando los datos importados.** (Ver archivo `4.png` en el directorio `work_2/screenshots/`.)
- **Captura de pantalla de la ejecución de las consultas `check_missing_values` y `check_duplicate_values` mostrando los resultados (0 y tabla vacía, respectivamente).** (Ver archivo `5.png` y `6.png` en el directorio `work_2/screenshots/`.)
- **Captura de pantalla de `silver_layer` con todas las tablas dimensionales y de hechos.** (Ver archivo `7.png` en el directorio `work_2/screenshots/`.)
- **Captura de pantalla de `golden_layer.payment_data` con `View/Edit Data` mostrando la columna `payment_amount` calculada.** (Ver archivo `8.png` en el directorio `work_2/screenshots/`.)
- **Captura de pantalla de `golden_layer.technical_data` con `View/Edit Data` mostrando la columna `technical_issue`.** (Ver archivo `9.png` en el directorio `work_2/screenshots/`.)
- **Captura de pantalla de `golden_layer.non_pii_data` con `View/Edit Data` mostrando los datos enmascarados.** (Ver archivo `10.png` en el directorio `work_2/screenshots/`.)
- **Captura de pantalla de `golden_layer.pii_data` con `View/Edit Data` mostrando los datos completos sin enmascarar.** (Ver archivo `11.png` en el directorio `work_2/screenshots/`.)

---

## 3. Conclusiones 

Con esta actividad se pudo implementar un pipeline ETL completo para la empresa LeadData, transformando datos brutos en información estructurada y útil para diferentes departamentos, con consideraciones de seguridad y privacidad de datos. Así mismo, las capas Bronze, Silver y Golden son funcionales y contienen los datos según las especificaciones. 

Fue sumamente interesante ser partícipe en este proceso, el cual ya sabía como funcionaba por una materia que cursé en la carrera peroque jamás había llevado a la práctica de esta manera. Me gustó mucho y espero seguir aprendiendo más del mundo de los datos.