import os
import asyncio
from fastapi import FastAPI
from tapo import ApiClient  # type: ignore
from pydantic import BaseModel
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI()

# Conexión a tu cuenta Tapo usando las variables de entorno
client = ApiClient(os.getenv("TAPO_USER"), os.getenv("TAPO_PASS"))

# Define las IPs de las bombillas
device_ips = ["172.20.10.5", "172.20.10.4"]

# Inicializa controladores de dispositivos
devices = {}

async def init_devices():
    """Conecta con las bombillas usando sus IPs."""
    global devices
    devices = {}
    for ip in device_ips:
        try:
            devices[ip] = await client.l530(ip)
            print(f"✅ Conectado a bombilla {ip}")
        except Exception as e:
            print(f"❌ No se pudo conectar a {ip}: {e}")

@app.on_event("startup")
async def startup_event():
    """Inicializa los dispositivos al arrancar la aplicación."""
    await init_devices()

# Modelos para peticiones
class ColorRequest(BaseModel):
    hue: int
    saturation: int

class BrightnessRequest(BaseModel):
    brightness: int

# Endpoints

@app.post("/on")
async def encender():
    """Enciende todas las bombillas."""
    await asyncio.gather(*(device.on() for device in devices.values()))
    return {"status": "bombillas encendidas"}

@app.post("/off")
async def apagar():
    """Apaga todas las bombillas."""
    await asyncio.gather(*(device.off() for device in devices.values()))
    return {"status": "bombillas apagadas"}

@app.post("/cambiar_color")
async def cambiar_color(req: ColorRequest):
    """Cambia el color de todas las bombillas."""
    try:
        print(f"Cambiando color a hue {req.hue} y saturación {req.saturation}")
        await asyncio.gather(*(device.set_hue_saturation(req.hue, req.saturation) for device in devices.values()))
        print("Color cambiado correctamente")
        return {"status": f"color cambiado a hue {req.hue}, saturación {req.saturation}"}
    except Exception as e:
        print(f"Error al cambiar color: {e}")
        return {"status": "Error al cambiar el color"}

@app.post("/brightness")
async def cambiar_brillo(req: BrightnessRequest):
    """Cambia el brillo de todas las bombillas."""
    await asyncio.gather(*(device.set_brightness(req.brightness) for device in devices.values()))
    return {"status": f"brillo cambiado a {req.brightness}"}
