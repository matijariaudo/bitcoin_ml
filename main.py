#Librerías necesarias
from fastapi import FastAPI, Request , Body, Query
from fastapi.responses import JSONResponse ,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3 
#Helpers de código
import time
import os
#Código propio
import scripts.database #crea la bd si no existe
from scripts.prices import start_timer, getPrices

############################### Database - SQLite ###############################################
DB_PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep
DB_FILE_PATH = f'{DB_PATH}database{os.sep}database.db'

############################### Inicio API ##############################################


app = FastAPI()

# Static & Templates (como Flask)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/suscribirse")
def suscribirse(payload: dict = Body(...)):
    print(f"payload {payload}")
    email = (payload.get("email") or "").strip().lower()
    print(f"email {email}")
    if not email:
        return JSONResponse({"ok": False, "msg": "Email requerido"}, status_code=400)
    try:
        with sqlite3.connect(DB_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                        INSERT INTO subscribers (email, status) VALUES (:email, 1)
                        ON CONFLICT(email) DO UPDATE SET email = :email, status = 1
                        """, 
                        {"email": email})
            conn.commit()
            return JSONResponse({"ok": True, "msg": "Suscripción activada", "email": email}, status_code=200)
    except Exception as e:
        return JSONResponse({"ok": False, "msg": f"Error suscribiendo: {e}"}, status_code=500)

@app.get("/desuscribir", response_class=HTMLResponse)
def unsubscribe(email: str = Query(default="")):
    email = (email or "").strip().lower()
    if not email:
        return HTMLResponse("<h3>Email requerido</h3>", status_code=400)
    try:
        with sqlite3.connect(DB_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE subscribers SET status = 0 WHERE email = ?", (email,))
            conn.commit()
        return HTMLResponse(f"<h3>El email {email} ha sido dado de baja correctamente.</h3>", status_code=200)
    except Exception as e:
        return HTMLResponse(f"<h3>Error al desuscribir: {e}</h3>", status_code=500)

@app.get("/prediction")
def sendPrediction():
    
    return JSONResponse(getPrices(),status_code=200)

from datetime import datetime, timedelta

@app.get('/predictionlist')
async def getList():
    cutoff_timestamp = int(time.time()) - 60*60*24   # hace 24 horas
    cutoff_datetime = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_FILE_PATH) as conn:
        conn.row_factory = sqlite3.Row  # para acceder por nombre de columna
        cur = conn.cursor()

        try:
            # si fecha es timestamp INTEGER
            cur.execute(
                "SELECT * FROM predictions WHERE fecha >= ? ORDER BY fecha DESC LIMIT 20",
                (cutoff_timestamp,)
            )
            data = cur.fetchall()
        except Exception:
            # si fecha es DATETIME string
            cur.execute(
                "SELECT * FROM predictions WHERE fecha >= ? ORDER BY fecha DESC LIMIT 20",
                (cutoff_datetime,)
            )
            data = cur.fetchall()

    send = [
        {
            "id": row["id"],
            "date": row["fecha"],
            "price": row["price"],
            "lowest_price": row["lowest_price"],
            "prediction": row["prediction"],
            "prediction_prob": row["prediction_prob"]
        }
        for row in data
    ]
    return JSONResponse(content=send, status_code=200)

@app.on_event("startup")
def functionA():
    start_timer()
    print("The machine has started to check the price")

@app.get("/test")
def test():
    return {"status": r.status_code, "content": r.text, "data":getPrices()}




