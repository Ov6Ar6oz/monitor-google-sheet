import os
import hashlib
import requests

SHEET_URL = "https://docs.google.com/spreadsheets/d/1etnphAtuO43y3TWPQSyaRv3nlpS2JvQl/export?format=csv"

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

r = requests.get(SHEET_URL, timeout=30)
contenido = r.text

print("CSV descargado correctamente")

hash_actual = hashlib.sha256(
    contenido.encode("utf-8")
).hexdigest()

archivo_hash = "ultimo_hash.txt"

hash_anterior = ""

if os.path.exists(archivo_hash):
    with open(archivo_hash, "r") as f:
        hash_anterior = f.read().strip()

if hash_actual != hash_anterior:
    
print("Cambio detectado, enviando mensaje...")

    requests.post(
        print("Mensaje enviado")

        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": "🚨 Se detectó un cambio en la hoja de Google Sheets."
        },
        timeout=30
    )

    with open(archivo_hash, "w") as f:
        f.write(hash_actual)
