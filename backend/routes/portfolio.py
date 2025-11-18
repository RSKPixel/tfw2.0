from fastapi import APIRouter
from fastapi.responses import JSONResponse
from config import kite_connect, postgres_engine

router = APIRouter(prefix="/portfolio")


@router.get("/profile")
async def get_portfolio_profile():
    kite = kite_connect()
    profile = kite.profile()
    return JSONResponse(content={"status": "success", "data": profile}, status_code=200)


@router.get("/holdings")
async def get_portfolio_holdings():
    kite = kite_connect()

    holdings = kite.holdings()

    return JSONResponse(
        content={"status": "success", "data": holdings}, status_code=200
    )


@router.get("/positions")
async def get_portfolio_positions():
    kite = kite_connect()

    positions = kite.positions()

    return JSONResponse(
        content={"status": "success", "data": positions}, status_code=200
    )


@router.get("/funds")
async def get_portfolio_funds():
    kite = kite_connect()

    funds = kite.margins()

    return JSONResponse(content={"status": "success", "data": funds}, status_code=200)


@router.get("/trades")
async def get_portfolio_trades():
    kite = kite_connect()

    trades = kite.trades()

    return JSONResponse(content={"status": "success", "data": trades}, status_code=200)
