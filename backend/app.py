import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core import fetch_symbols, fetch_ohlcv
from datetime import datetime, timedelta

origins = [
    "http://localhost:5173",
]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(404)
def not_found_handler(request: Request, exc):
    return Response(content="Custom 404: Resource not found", status_code=404)


@app.get("/symbols")
def get_symbols():

    symbols = fetch_symbols()

    return JSONResponse(content=list(symbols["symbol"]), status_code=200)


@app.get("/ohlcv")
def get_ohlcv(
    symbol: str = "NIFTY-I",
    start_date: str = (datetime.now() - timedelta(days=300)).strftime("%Y-%m-%d"),
    end_date: str = datetime.now().strftime("%Y-%m-%d"),
    timeframe: str = "1day",
):
    df = fetch_ohlcv(symbol, start_date, end_date, timeframe)
    data = json.loads(df.to_json(orient="records", date_format="iso"))

    return JSONResponse(content=data, status_code=200)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
