# Flask Web Bluetooth Scanner

Aplicación web que permite escanear dispositivos Bluetooth desde una interfaz web utilizando Flask como backend y Bleak para la comunicación Bluetooth.

## Dependencias principales

- **Flask**: Framework web ligero para Python.
- **Bleak**: Biblioteca para comunicación Bluetooth en Python.
- **Hypercorn**: Servidor ASGI.
- **Asyncio**: Para la ejecucion de las tareas asincronas en segundo plano.

## Formas de instalacion

### 1. Entorno virtual de Python (venv)

1. Crear y activar entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Usando UV

1. Instalar dependencias:
   ```bash
   uv sync
   ```

## Formas de Ejecucion
1. Ejecutar la app (dentro del entorno):
   ```bash
   python app.py
   ```

2. Ejecutar con Hypercorn (dentro del entorno):
   ```bash
   hypercorn app:asgi_app
   ```

2. Ejecutar con Hypercorn:
   ```bash
   uv run app
   ```

### 3. Instalacion y Ejecucion usando Docker Compose

```bash
docker compose up app
```

## Endpoints principales

- **/**  
  Interfaz web principal donde se listan los dispositivos bluetooth.

- **/start_scan**  
  Inicia el escaneo en segundo plano.

- **/stop_scan**  
  Inicia el escaneo en segundo plano.

- **/devices**  
  Devuelve la lista de dispositivos encontrados en formato JSON.

---

**Notas:**  
- El bluetooth debe estar correctamente instalado y encendido.
- Esta aplicación fue probada únicamente en Linux Mint. El funcionamiento en otros sistemas operativos no está garantizado.