from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from joblib import load
from binance import get_binance_input_row
import pandas as pd
import json

app = FastAPI()

# Static & Templates (como Flask)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Cargar modelos
xgb_model = load('models/xgb_model_24.pkl')
preprocessor=load('models/preprocessor.pkl')

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict():
    # Obtener datos de Binance
    df_input = get_binance_input_row()
    cols_0 = [col for col in df_input.columns if col.endswith('_0')]
    values = df_input.loc[0, cols_0].to_dict()
    
    # Convertir a array
    #x = df_input.values.reshape(1, -1)
    x = df_input.copy()

    # Predicciones individuales
    x = preprocessor.transform(x)
    p2 = xgb_model.predict_proba(x)[:, 1]

    # Ensamble
    y_final = int(p2 > 0.7)

    return JSONResponse({"probability": float(p2), "prediction": y_final, "data": values})