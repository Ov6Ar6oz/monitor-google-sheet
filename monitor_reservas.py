import os
import json
import requests
from datetime import datetime

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SPREADSHEET_ID = "1qO4bbo8qNriFxGZz-k5VHx5A4XaNqfgoL8dLempDhF4"

GIDS = {
    4: ("Viernes", "750539006"),
    5: ("Sabado", "1595785792"),
    6: ("Domingo", "794348104")
}

nombre_dia = "Viernes"
gid = "750539006"

CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={gid}"
)

print(f"Leyendo hoja: {nombre_dia}")

csv_actual = requests.get(CSV_URL, timeout=30).text

ESTADO_ACTUAL = "estado_actual.csv"
ESTADO_ANTERIOR = "estado_anterior.csv"

with open(ESTADO_ACTUAL, "w", encoding="utf-8") as f:
    f.write(csv_actual)

if not os.path.exists(ESTADO_ANTERIOR):
    with open(ESTADO_ANTERIOR, "w", encoding="utf-8") as f:
        f.write(csv_actual)

    print("Estado inicial guardado.")
    exit(0)

with open(ESTADO_ANTERIOR, "r", encoding="utf-8") as f:
    csv_anterior = f.read()

lineas_anteriores = csv_anterior.splitlines()
lineas_actuales = csv_actual.splitlines()

max_lineas = min(len(lineas_anteriores), len(lineas_actuales))

actividad_detectada = ""
horario_actual = ""

avisos = []

for i in range(max_lineas):

    actual = lineas_actuales[i]

    if "BICICLETA" in actual.upper():
        actividad_detectada = "🚲 Bicicleta"

    if "KAYAKS" in actual.upper():
        actividad_detectada = "🚣 Kayaks"

    if "ARCO Y FLECHA" in actual.upper():
        actividad_detectada = "🏹 Arco y Flecha"

    partes = [x.strip() for x in actual.split(",")]

    if len(partes) >= 3:

        if "hs" in partes[0]:
            horario_actual = partes[0]

    anterior = lineas_anteriores[i]
    actual = lineas_actuales[i]

    if anterior == actual:
        continue

    partes_ant = [x.strip() for x in anterior.split(",")]
    partes_act = [x.strip() for x in actual.split(",")]

    if len(partes_act) < 3:
        continue

    actividad_detectada = ""
    puesto = ""
    habitacion_ant = ""
    habitacion_act = ""
    nombre = ""

    # BICICLETA
    if len(partes_act) > 1 and partes_act[1]:

        actividad_detectada = "🚲 Bicicleta"

        puesto = partes_act[0]

        habitacion_act = partes_act[1]

        if len(partes_ant) > 1:
            habitacion_ant = partes_ant[1]

        if len(partes_act) > 2:
            nombre = partes_act[2]

    # ARCO Y FLECHA
    elif len(partes_act) > 5 and partes_act[5]:

        actividad_detectada = "🏹 Arco y Flecha"

        puesto = partes_act[4]

        habitacion_act = partes_act[5]

        if len(partes_ant) > 5:
            habitacion_ant = partes_ant[5]

        if len(partes_act) > 6:
            nombre = partes_act[6]

    # KAYAKS
    elif len(partes_act) > 9 and partes_act[9]:

        actividad_detectada = "🚣 Kayaks"

        puesto = partes_act[8]

        habitacion_act = partes_act[9]

        if len(partes_ant) > 9:
            habitacion_ant = partes_ant[9]

        if len(partes_act) > 10:
            nombre = partes_act[10]

    else:
        continue
        
    # Nueva reserva
    if habitacion_ant == "" and habitacion_act != "":

        mensaje = (
            "🏨 Nueva reserva\n\n"
            f"📅 {nombre_dia}\n"
            f"{actividad_detectada}\n"
            f"🕒 {horario_actual}\n"
            f"🎫 Puesto {puesto}\n"
            f"🏠 Habitación {habitacion_act}"
        )

        if nombre:
            mensaje += f"\n👤 {nombre}"

        avisos.append(mensaje)

    # Cancelación
    elif habitacion_ant != "" and habitacion_act == "":

        mensaje = (
            "❌ Reserva cancelada\n\n"
            f"📅 {nombre_dia}\n"
            f"{actividad_detectada}\n"
            f"🕒 {horario_actual}\n"
            f"🎫 Puesto {puesto}\n"
            f"🏠 Habitación {habitacion_ant}"
        )

        avisos.append(mensaje)

for aviso in avisos:

    print(aviso)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": aviso
        },
        timeout=30
    )

with open(ESTADO_ANTERIOR, "w", encoding="utf-8") as f:
    f.write(csv_actual)

print(f"Avisos enviados: {len(avisos)}")
