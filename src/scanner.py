import asyncio
import base64
from enum import Enum
from typing import Callable, Dict, Tuple

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from werkzeug.exceptions import BadRequest, InternalServerError, Locked

from src.company_identifier import CompanyIdentifiers
from src.logger import logger


class ScannerState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    STOPPING = "stopping"


class BLEScanner:
    def __init__(self) -> None:
        self._scanner: BleakScanner | None = None
        self._state = ScannerState.STOPPED
        self._stop_event = asyncio.Event()
        self._company_identifiers = CompanyIdentifiers()

    @property
    def scanner(self) -> BleakScanner:
        if not self._scanner:
            self._scanner = BleakScanner(
                detection_callback=self._detection_callback(), scanning_mode="active"
            )
        return self._scanner

    @property
    def is_running(self) -> bool:
        return self._state == ScannerState.RUNNING

    async def start_scan(self):
        try:
            if self.is_running:
                raise Locked(
                    "El escáner ya está en ejecución. Detén el escáner antes de iniciar uno nuevo."
                )

            logger.info("Iniciando el escáner BLE...")

            self._stop_event.clear()

            await self.scanner.start()
            self._state = ScannerState.RUNNING

            logger.info("Escáner BLE iniciado.")
            await self._stop_event.wait()

        except Exception as e:
            logger.error(f"Error al iniciar el escáner: {e}")
            raise InternalServerError(description="Error al iniciar el escáner")
        finally:
            await self.scanner.stop()
            self._state = ScannerState.STOPPED
            logger.info("Escáner BLE detenido.")

    async def stop_scan(self):
        try:
            if not self.is_running:
                raise BadRequest(
                    status_code=400, detail="El escáner no está en ejecución."
                )
            logger.info("Deteniendo el escáner BLE...")

            self._stop_event.set()
            self._state = ScannerState.STOPPING

            logger.info("Esperando a que el escáner se detenga...")
        except Exception as e:
            logger.error(f"Error al detener el escáner: {e}")
            raise InternalServerError(description="Error al detener el escáner")

    def get_devices(self) -> list:
        if self._state != ScannerState.RUNNING:
            return []

        devices: Dict[str, Tuple[BLEDevice, AdvertisementData]] = (
            self.scanner.discovered_devices_and_advertisement_data
        )
        devices_formated = []
        for address, (device, ad_data) in devices.items():
            manufacturer_data_list = self._parse_manufacturer_data(ad_data)

            device_info = {
                "address": address,
                "name": device.name or "Desconocido",
                "manufacturer_id": "N/A",
                "manufacturer_name": "N/A",
                "manufacturer_data": "N/A",
            }

            if manufacturer_data_list:
                first_md = manufacturer_data_list[0]
                device_info["manufacturer_id"] = first_md.get(
                    "manufacturer_id_hex", "N/A"
                )
                device_info["manufacturer_name"] = first_md.get(
                    "manufacturer_name", "N/A"
                )
                device_info["manufacturer_data"] = first_md.get("data_hex", "N/A")

            devices_formated.append(device_info)

        return devices_formated

    def _detection_callback(self) -> Callable[..., None]:
        def callback(device: BLEDevice, advertising_data: AdvertisementData) -> None:
            manufacturer_data = self._parse_manufacturer_data(advertising_data)
            logger.info(f"Dispositivo detectado: {device.address} - {device.name}")
            logger.info(f"Advertising Data: {advertising_data}")
            logger.info("Datos del fabricante:")
            for md in manufacturer_data:
                logger.info(
                    f"  ID: {md['manufacturer_id']} ({md['manufacturer_id_hex']}) - "
                    f"Nombre: {md['manufacturer_name']}"
                )

        return callback

    def _parse_manufacturer_data(
        self, advertisement_data: AdvertisementData
    ) -> list[dict]:
        manufacturer_data = []
        for manufacturer_id, data in advertisement_data.manufacturer_data.items():
            manufacturer_name = self._company_identifiers.get(manufacturer_id)
            data_b64 = base64.b64encode(data).decode("utf-8")
            manufacturer_data.append(
                {
                    "manufacturer_id": manufacturer_id,
                    "manufacturer_id_hex": f"{manufacturer_id:04x}",
                    "manufacturer_name": manufacturer_name,
                    "data_hex": data.hex() or "N/A",
                    "data_base64": data_b64 or "N/A",
                }
            )
        return manufacturer_data
