from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from joblib import load
from fastapi import HTTPException
from binance import get_binance_input_row
import requests
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
    try:
        df_input = get_binance_input_row()

        if df_input.empty or len(df_input) < 1:
            raise HTTPException(status_code=503, detail="Datos insuficientes desde Binance")

        cols_0 = [col for col in df_input.columns if col.endswith('_0')]
        values = df_input.loc[0, cols_0].to_dict()

        x = df_input.copy()
        x = preprocessor.transform(x)
        p2 = xgb_model.predict_proba(x)[:, 1]
        y_final = int(p2 > 0.7)

        return JSONResponse({"probability": float(p2), "prediction": y_final, "data": values})

    except HTTPException:
        raise  # vuelve a lanzar el error tal cual
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test():
    try:
        r = requests.get("https://api.binance.com/api/v3/ping", timeout=3)
        return {"status": r.status_code, "content": r.text}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}