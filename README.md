---

# Proyecto: Forecast de Ventas y Propuesta de Pedidos

Este proyecto tiene como objetivo procesar y transformar datos de Excel provenientes de diferentes fuentes (saldo, UH, MyStore) para calcular proyecciones de ventas y generar propuestas de pedidos. Se realizan diversas operaciones como el cálculo de promedios diarios, ajuste de ventas según el canal web y MyStore (reservas desde offline al stock de online), asignación de KAM (Key Account Manager) según departamentos y exportación de resultados en archivos Excel para cada segmento.

---

## Índice

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Guía de Uso y Ejecución](#guía-de-uso-y-ejecución)
- [Explicación del Código](#explicación-del-código)
- [Licencia](#licencia)

---

## Descripción del Proyecto

Este script realiza las siguientes tareas:

1. **Carga de datos:** Se importan tres archivos Excel: `saldo.xlsx`, `uh.xlsx` y `mystore.xlsx`.
2. **Transformación y limpieza:** Se renombran columnas, se eliminan filas/columnas innecesarias y se formatean los datos.
3. **Cálculos y predicciones:**
   - Cálculo de promedios de ventas diarias (tanto para total MM como para el canal web).
   - Previsión de venta mediante una función que ajusta según las tendencias de cada producto, el departameno, parámetros estacionales y comportamiento de venta del canal online y offline.
   - Generación de propuestas de pedidos, teniendo en cuenta el stock actual, los pedidos pendientes y las necesidades futuras.
4. **Asignación de KAM:** Se asigna un KAM específico (por ejemplo, "foto", "audio" o "tv") según el departamento.
5. **Exportación:** Se generan diferentes archivos Excel para cada KAM y un archivo adicional para gestionar solicitudes de transferencias del almacén de gran carga (UH) al almacén de online.

---

## Requisitos Previos

- **Python 3.x:** Asegúrate de tener una versión reciente de Python.
- **Librerías Python:** Se utilizan las siguientes librerías:
  - `numpy`
  - `pandas`
  - `re`
  - `warnings`
  - `datetime`
  - `calendar`

Puedes instalarlas (si no las tienes) usando pip:

```bash
pip install numpy pandas
```

*Nota:* Las librerías `re`, `warnings`, `datetime` y `calendar` son módulos estándar de Python.

- **Archivos de Datos:** Debes contar con los siguientes archivos en la raíz del proyecto:
  - `saldo.xlsx`
  - `uh.xlsx`
  - `mystore.xlsx`

---

## Estructura del Proyecto

```
forecast-ventas/
├── data/
│   ├── saldo.xlsx
│   ├── uh.xlsx
│   └── mystore.xlsx
├── output/
│   ├── df_foto.xlsx
│   ├── df_audio.xlsx
│   ├── df_tv.xlsx
│   └── df_planner_uh_transfers.xlsx
├── scripts/
│   └── main.py
└── README.md
```

- **data/**: Carpeta para los archivos de entrada.
- **output/**: Carpeta donde se guardarán los archivos Excel generados.
- **scripts/**: Carpeta con el script principal del proyecto.
- **README.md**: Documentación del proyecto.

---

## Guía de Uso y Ejecución

1. **Abrir el proyecto en tu editor favorito:**  
   Puedes utilizar Visual Studio Code, PyCharm o el editor de tu preferencia.

2. **Ejecutar el script:**  
   Desde la terminal, ubícate en la carpeta `scripts/` y ejecuta:

   ```bash
   python main.py
   ```

   El script realizará los cálculos, generará las propuestas de pedido y exportará los resultados en la carpeta `output/`.

3. **Verificar resultados:**  
   Revisa los archivos Excel generados:
   - `df_foto.xlsx`
   - `df_audio.xlsx`
   - `df_tv.xlsx`
   - `df_planner_uh_transfers.xlsx`

---

## Explicación del Código

El código se organiza en varias secciones:

1. **Importación de Librerías y Configuración Inicial:**  
   Se importan librerías esenciales y se configuran los archivos de entrada (saldo, uh y mystore).
   Las librerias utilizadas han sido:
- numpy
- pandas
- re
- datetime
- calendar
- warnings

3. **Funciones Auxiliares:**
   - **ultimas_ventas:** Extrae las columnas con las ventas recientes según el periodo.
   - **dias_mes_pasado:** Retorna el número de días del mes anterior.
   - **prevision_venta:** Calcula la previsión de venta aplicando ajustes según el departamento y parámetros estacionales.
   - **asignar_kam:** Asigna un KAM según el departamento.
   - **kam_df:** Filtra el DataFrame según el KAM.

4. **Carga y Transformación de Datos:**  
   Se leen los archivos Excel y se realizan operaciones de limpieza y transformación de datos.
  - Eliminación de NAs
  - Eliminación de productos reacondicionados.
  - Selección de las columnas de interés.
  - Conversión de formatos.

5. **Cálculos y Proyecciones:**  
   Se calcula:
   - El stock total sumando distintas fuentes.
   - El promedio diario de ventas para distintos canales (Total comercio y online).
   - La previsión de ventas de las tiendas físicas y como estas se nutrirán del almacén de online (según el tipo de producto).
   - La previsión de ventas de online que se nutrirá de las distintas tiendas físicas en lugar de restar stock del almacén de online.
   - El ajuste estacional (ajusta la proyección de las ventas según la época del año y el tipo de producto).
   - La propuesta de pedido ajustada según stock, pedidos pendientes y previsión.
   - La asignación de KAM y la solicitud de transferencias en el caso de UH.

6. **Exportación:**  
   Se generan archivos Excel para cada KAM con aquellos productos que tienen necesidades de reposición, así como la planificación de transferencias entre distintos almacenes para los prodcutos de gran carga.

---


## Licencia

Este proyecto se distribuye bajo la licencia [MIT](license.txt).  
