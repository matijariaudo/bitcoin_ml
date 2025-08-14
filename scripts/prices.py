from scripts.binance import get_binance_input_row #importar datos binance
from scripts.send_email import send_email
from joblib import load #importar modelos
#Helpers de código
import pandas as pd
import asyncio
import time
import os
import sqlite3 

############################### Global var ###############################################
current_data={} #variable para tener en memoria los datos actuales de predicción de binance

############################### Database - SQLite ###############################################
DB_PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep
DB_FILE_PATH = f'../database.db'

############################### Cargar modelos ###############################
xgb_model = load('models/xgb_model_24.pkl')
preprocessor=load('models/preprocessor.pkl')

############################### Price ML model - checking ########################################
async def timer():
    while True:
        data = await checkPrice()  # esperar la corrutina
        if "error" in data:
            print("Hubo un error:", data["error"])
        else:
            #print("Predicción:", data["prediction"], "Probabilidad:", data["probability"])
            pred = int(data["prediction"])          
            prob = float(data["probability"])
            precio= float(data['current_price'])
            fecha = float(data["open_time"])  
            with sqlite3.connect(DB_FILE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO predictions (fecha, precio, precio_min_4h, prediction, probability) 
                    VALUES (:fecha, :precio, 0, :pred, :prob)
                    ON CONFLICT(fecha) DO UPDATE SET precio = :precio;
                    """,
                    {"fecha": fecha, "precio": precio, "pred": pred, "prob": prob}
                )
                conn.commit()
            ##Guardar precio + bajo
            #print("Precio: ",precio)
            savePrice(precio)
            ##Enviar email
            send_signal_emails()    
        await asyncio.sleep(10)  # espera 1 minuto

def start_timer():
    #return True
    asyncio.create_task(timer())

################### HELPERS #############################################

async def checkPrice():
    try:
        df_input = get_binance_input_row()
        if df_input.empty or len(df_input) < 1:
            raise ValueError("Datos insuficientes desde Binance")
        cols_0 = [col for col in df_input.columns if col.endswith('_0')]
        values = df_input.loc[0, cols_0].to_dict()
        global current_data
        current_data=values  
        x = df_input.copy()
        x = preprocessor.transform(x)
        p2 = xgb_model.predict_proba(x)[:, 1]
        y_final = int(p2 > 0.7)
        current_data['prediction']=y_final
        current_data['prediction_prob']=float(p2)
        return {"probability": float(p2), "prediction": y_final, "data": values, "current_price":values["close_0"],"open_time":values['open_time_0']}
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

########### Check DB ################################
def savePrice(price):
    #print("Buscando los datos")
    with sqlite3.connect(DB_FILE_PATH) as conn:
        db=pd.read_sql(f"Select * from predictions where fecha >={int(time.time()-60*60*4)}",conn)   
    for i, row in db[(db['precio_min_4h']>price) | (db['precio_min_4h']==0)].iterrows():
        with sqlite3.connect(DB_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE predictions SET precio_min_4h = ? WHERE id = ?",
                (float(price), int(row['id']))
            )
            conn.commit()
    

# ### codigo nuevo### (lógica de envío de señales + endpoints de suscripción)
def _now_epoch() -> float:
    return float(time.time())

def _last_sent_at(subscriber_id: int):
    with sqlite3.connect(DB_FILE_PATH) as conn:
        row = conn.execute(
            "SELECT MAX(sent_at) FROM sent_emails WHERE subscriber_id = ?",
            (subscriber_id,)
        ).fetchone()
    return row[0] if row and row[0] is not None else None

def send_signal_emails():
    try:
        pred = int(current_data.get("prediction", 0))
        if pred != 1:
            return  # Solo enviamos cuando la predicción es positiva

        price = current_data.get("close_0")
        prob = current_data.get("prediction_prob")
        open_time = current_data.get("open_time_0")

        subject = "Señal BTC: PREDICCIÓN POSITIVA"
        body = (
            "Hay una nueva señal positiva (prediction = 1).\n"
            f"Precio actual (close_0): {price}\n"
            f"Probabilidad del modelo: {prob}\n"
            f"Open time: {open_time}\n\n\n\n"
            f"Para desubscribte ingresa a : http://18.230.227.217:8000/desuscribir?email=TUEMAIL -> Modifica con tu email\n"
        )
        with sqlite3.connect(DB_FILE_PATH) as conn:
            subs = conn.execute(
                "SELECT id, email FROM subscribers WHERE status = 1"
            ).fetchall()

        now_ts = _now_epoch()
        four_hours = 4 * 60 * 60

        for sub in subs:
            sub_id, email = sub[0], sub[1]
            last = _last_sent_at(sub_id)
            if last is None or (now_ts - last) >= four_hours:
                try:
                    send_email(email, subject, body)
                    conn.execute(
                        "INSERT INTO sent_emails (subscriber_id, sent_at) VALUES (?, ?)",
                        (sub_id, now_ts)
                    )
                    conn.commit()
                except Exception as e:
                    print(f"[send_signal_emails] Error enviando a {email}: {e}")
    except Exception as e:
        print(f"[send_signal_emails] Error general: {e}")

#### fin codigo nuevo###

def getPrices():
    global current_data
    return current_data