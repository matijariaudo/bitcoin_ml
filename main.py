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

@app.get('/predictionlist')
async def getList():
    with sqlite3.connect(DB_FILE_PATH) as conn:
        data=conn.execute(f"Select * from predictions where fecha>={int(time.time()-60*60*24)}").fetchall()
    send=[]
    for i in data:
        send.append({"id":i[0],"date":i[1],"price":i[2],"lowest_price":i[3],"prediction":i[4],"prediction_prob":i[5]})
    return JSONResponse(content=send,status_code=200)

@app.on_event("startup")
def functionA():
    start_timer()
    print("The machine has started to check the price")

@app.get("/test")
def test():
    return {"status": r.status_code, "content": r.text, "data":getPrices()}




