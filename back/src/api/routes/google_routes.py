from fastapi import APIRouter, Query
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

router = APIRouter(prefix="/google", tags=["Maps"])

@router.get("/clinicas_cercanas")
def buscar_clinicas(lat: float = Query(...), lon: float = Query(...), radio: int = 3000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radio,
        "type": "hospital",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    resultados = []
    for lugar in data.get("results", []):
        resultados.append({
            "nombre": lugar["name"],
            "direccion": lugar.get("vicinity"),
            "ubicacion": lugar["geometry"]["location"]
        })

    return resultados
