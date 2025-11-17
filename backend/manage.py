import json
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes.data import router as data
from routes.portfolio import router as portfolio

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

app.include_router(data)
app.include_router(portfolio)


if __name__ == "__main__":
    uvicorn.run("manage:app", host="127.0.0.1", port=8000, reload=True)
