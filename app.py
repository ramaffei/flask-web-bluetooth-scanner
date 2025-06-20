import asyncio

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, render_template
from hypercorn.asyncio import serve
from hypercorn.config import Config

from src.scanner import BLEScanner

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)

logger = app.logger
ble_scanner = BLEScanner()


@app.route("/")
async def index():
    return render_template("index.html")


@app.route("/start_scan", methods=["POST"])
async def start_scan() -> dict:
    asyncio.create_task(ble_scanner.start_scan())
    return {"status": "success", "message": "Escaneo iniciado."}, 202


@app.route("/stop_scan", methods=["POST"])
async def stop_scan() -> dict:
    await ble_scanner.stop_scan()
    return {"status": "success", "message": "Escaneo detenido."}, 202


@app.route("/devices", methods=["GET"])
def get_devices_list() -> dict:
    return {"devices": ble_scanner.get_devices()}, 200


if __name__ == "__main__":
    asyncio.run(serve(asgi_app, Config()))
