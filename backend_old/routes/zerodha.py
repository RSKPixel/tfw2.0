from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from config import kite_connect, postgres_engine
from psycopg2.extras import execute_values
import pandas as pd
import numpy as np
from io import BytesIO

router = APIRouter(prefix="/zerodha")


@router.get("/profile")
async def get_portfolio_profile():
    try:
        kite = kite_connect()
        profile = kite.profile()
        status = "success"
    except Exception as e:
        profile = {}
        status = "error"
    return JSONResponse(content={"status": status, "data": profile}, status_code=200)


@router.get("/holdings")
async def get_portfolio_holdings():
    kite = kite_connect()

    holdings = kite.holdings()

    return JSONResponse(
        content={"status": "success", "data": holdings}, status_code=200
    )


@router.get("/open-positions")
async def get_portfolio_positions(user_id: str):
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


@router.get("/tradebook")
async def get_portfolio_tradebook(user_id: str):
    psql_engine = postgres_engine()
    query = """
    SELECT trade_id, symbol, trade_date, exchange, segment,
           trade_type, auction, quantity, price, order_id,
           order_execution_time, expiry_date, broker, user_id
    FROM fno_tradebook
    WHERE user_id = %s
    ORDER BY trade_date DESC, order_execution_time DESC
    """
    df = pd.read_sql_query(query, psql_engine, params=(user_id,))
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)

    data = df[:5].to_dict(orient="records")

    return JSONResponse(content={"status": "success", "data": data}, status_code=200)


@router.post("/tradebook-upload")
async def upload_tradebook(
    file: UploadFile = File(...), user_id: str = Form(...), broker: str = Form(...)
):

    psql_engine = postgres_engine()

    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        df["user_id"] = user_id
        df["broker"] = broker

        cols = [
            "symbol",
            "isin",
            "trade_date",
            "exchange",
            "segment",
            "series",
            "trade_type",
            "auction",
            "quantity",
            "price",
            "trade_id",
            "order_id",
            "order_execution_time",
            "expiry_date",
            "user_id",
            "broker",
        ]

        records = [tuple(row[col] for col in cols) for _, row in df.iterrows()]
        stmt = """
        INSERT INTO fno_tradebook (
            symbol,
            isin,
            trade_date,
            exchange,
            segment,
            series,
            trade_type,
            auction,
            quantity,
            price,
            trade_id,
            order_id,
            order_execution_time,
            expiry_date,
            user_id,
            broker
        )
        VALUES %s
        ON CONFLICT (trade_id, trade_date)
        DO UPDATE SET
            symbol               = EXCLUDED.symbol,
            isin                 = EXCLUDED.isin,
            exchange             = EXCLUDED.exchange,
            segment              = EXCLUDED.segment,
            series               = EXCLUDED.series,
            trade_type           = EXCLUDED.trade_type,
            auction              = EXCLUDED.auction,
            quantity             = EXCLUDED.quantity,
            price                = EXCLUDED.price,
            order_id             = EXCLUDED.order_id,
            order_execution_time = EXCLUDED.order_execution_time,
            expiry_date          = EXCLUDED.expiry_date,
            user_id              = EXCLUDED.user_id,
            broker               = EXCLUDED.broker;

        """

        raw_connection = psql_engine.raw_connection()
        try:
            cursor = raw_connection.cursor()
            execute_values(cursor, stmt, records, page_size=100)
            raw_connection.commit()

            pnl, positions = update_pnl_fifo(user_id, broker, df)
            save_pnl(user_id, broker, pnl)
            save_positions(user_id, broker, positions)
        finally:
            cursor.close()
            raw_connection.close()

    except Exception as e:
        print(e)
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=400
        )

    return JSONResponse(
        content={
            "status": "success",
            "message": "Trade book uploaded successfully",
            "data": [],
        },
        status_code=200,
    )


@router.get("/pnl-fifo")
async def pnl_fifo(user_id: str):
    psql_engine = postgres_engine()
    query = """
        SELECT * FROM fno_tradebook WHERE user_id = %s ORDER BY trade_date DESC, order_execution_time DESC
    """
    df = pd.read_sql_query(query, psql_engine, params=(user_id,))
    symbols = df["symbol"].unique().tolist()

    pnl, open_positions = update_pnl_fifo(user_id, "Zerodha", df)
    open_positions = open_positions.drop(columns=["isin", "series"])
    pnl, open_positions = pnl.round(2), open_positions.round(2)

    fno_pnl_delete_query = (
        """DELETE FROM fno_pnl WHERE user_id = %s AND symbol = ANY(%s)"""
    )

    fno_pnl_insert_query = """
        INSERT INTO fno_pnl (
            user_id, broker, symbol, exchange, segment, entry_date, exit_date,
            direction, quantity, lots, lot_size, buy_price, sell_price, buy_value,
            sell_value, gross_pnl, charges, net_pnl, model, remarks
        ) VALUES %s
    """
    records = [tuple(row) for _, row in pnl.iterrows()]

    raw_connection = psql_engine.raw_connection()
    try:
        cursor = raw_connection.cursor()
        cursor.execute(fno_pnl_delete_query, (user_id, symbols))
        raw_connection.commit()
        execute_values(cursor, fno_pnl_insert_query, records, page_size=100)
        raw_connection.commit()
    finally:
        cursor.close()
        raw_connection.close()

    insert_fno_positions_query = """
        INSERT INTO fno_positions (
            user_id, broker, symbol, trade_date, exchange, segment, trade_type,
            auction, quantity, price, order_id, trade_id, order_execution_time, expiry_date
        ) VALUES %s

    """
    open_positions["broker"] = "Zerodha"
    open_positions["user_id"] = user_id

    open_positions = open_positions[
        [
            "user_id",
            "broker",
            "symbol",
            "trade_date",
            "exchange",
            "segment",
            "trade_type",
            "auction",
            "quantity",
            "price",
            "order_id",
            "trade_id",
            "order_execution_time",
            "expiry_date",
        ]
    ]
    records = [tuple(row) for _, row in open_positions.iterrows()]
    print(records)

    delete_open_positions_query = """
        DELETE FROM fno_positions WHERE user_id = %s AND symbol = ANY(%s)
    """
    raw_connection = psql_engine.raw_connection()
    try:
        cursor = raw_connection.cursor()
        cursor.execute(delete_open_positions_query, (user_id, symbols))
        execute_values(cursor, insert_fno_positions_query, records, page_size=100)
        raw_connection.commit()
    finally:
        cursor.close()
        raw_connection.close()

    return JSONResponse(
        content={
            "status": "success",
            "data": {
                "pnl": pnl.to_dict(orient="records"),
                "open_positions": open_positions.to_dict(orient="records"),
            },
        },
        status_code=200,
    )


def save_pnl(user_id: str, broker: str, pnl: pd.DataFrame):
    psql_engine = postgres_engine()
    fno_pnl_delete_query = """DELETE FROM fno_pnl WHERE user_id = %s AND symbol = %s"""

    fno_pnl_insert_query = """
        INSERT INTO fno_pnl (
            user_id, broker, symbol, exchange, segment, entry_date, exit_date,
            direction, quantity, lots, lot_size, buy_price, sell_price, buy_value,
            sell_value, gross_pnl, charges, net_pnl, model, remarks
        ) VALUES %s
    """
    records = [tuple(row) for _, row in pnl.iterrows()]

    raw_connection = psql_engine.raw_connection()
    try:
        cursor = raw_connection.cursor()
        unique_symbols = pnl["symbol"].unique().tolist()
        for symbol in unique_symbols:
            cursor.execute(fno_pnl_delete_query, (user_id, symbol))
        raw_connection.commit()
        execute_values(cursor, fno_pnl_insert_query, records, page_size=100)
        raw_connection.commit()
    finally:
        cursor.close()
        raw_connection.close()


def save_positions(user_id: str, broker: str, open_positions: pd.DataFrame):
    psql_engine = postgres_engine()
    insert_fno_positions_query = """
        INSERT INTO fno_positions (
            user_id, broker, symbol, trade_date, exchange, segment, trade_type,
            auction, quantity, price, order_id, trade_id, order_execution_time, expiry_date
        ) VALUES %s

    """
    open_positions["broker"] = broker
    open_positions["user_id"] = user_id

    open_positions = open_positions[
        [
            "user_id",
            "broker",
            "symbol",
            "trade_date",
            "exchange",
            "segment",
            "trade_type",
            "auction",
            "quantity",
            "price",
            "order_id",
            "trade_id",
            "order_execution_time",
            "expiry_date",
        ]
    ]
    records = [tuple(row) for _, row in open_positions.iterrows()]

    delete_open_positions_query = """
        DELETE FROM fno_positions WHERE user_id = %s AND symbol = %s
    """
    raw_connection = psql_engine.raw_connection()
    try:
        cursor = raw_connection.cursor()
        unique_symbols = open_positions["symbol"].unique().tolist()
        for symbol in unique_symbols:
            cursor.execute(delete_open_positions_query, (user_id, symbol))
        execute_values(cursor, insert_fno_positions_query, records, page_size=100)
        raw_connection.commit()
    finally:
        cursor.close()
        raw_connection.close()


def update_pnl_fifo(user_id: str, broker: str, tradebook: pd.DataFrame):
    psql_engine = postgres_engine()
    unique_symbols = tradebook["symbol"].unique()

    tradebook.sort_values(by=["trade_date", "order_execution_time"], inplace=True)
    pnl = pd.DataFrame()
    open_positions = pd.DataFrame()

    for symbol in unique_symbols:
        trades = tradebook[tradebook["symbol"] == symbol]
        open_trades = pd.DataFrame(columns=trades.columns.tolist())

        for index, trade in trades.iterrows():
            lookfor = "sell" if trade["trade_type"] == "buy" else "buy"

            no_open_trades = open_trades[
                (open_trades["trade_type"] == lookfor) & (open_trades["quantity"] > 0)
            ].empty

            if no_open_trades:
                open_trades = pd.DataFrame([trade])
            else:
                for ot_index in open_trades.index:
                    if trade["quantity"] == 0:
                        break
                    qty = min(trade["quantity"], open_trades.at[ot_index, "quantity"])
                    trade["quantity"] -= qty
                    open_trades.at[ot_index, "quantity"] -= qty
                    entry_date = open_trades.at[ot_index, "trade_date"]
                    exit_date = trade["trade_date"]
                    buy_price = (
                        open_trades.at[ot_index, "price"]
                        if lookfor == "buy"
                        else trade["price"]
                    )
                    sell_price = (
                        trade["price"]
                        if lookfor == "buy"
                        else open_trades.at[ot_index, "price"]
                    )
                    direction = "LONG" if lookfor == "buy" else "SHORT"

                    pnl_record = {
                        "user_id": user_id,
                        "broker": broker,
                        "symbol": trade["symbol"],
                        "exchange": trade["exchange"],
                        "segment": trade["segment"],
                        "entry_date": entry_date,
                        "exit_date": exit_date,
                        "direction": direction,
                        "quantity": qty,
                        "lots": 1,
                        "lot_size": qty,
                        "buy_price": buy_price,
                        "sell_price": sell_price,
                        "buy_value": qty * buy_price,
                        "sell_value": qty * sell_price,
                        "gross_pnl": qty * (sell_price - buy_price),
                        "charges": 0.0,
                        "net_pnl": 0.0,
                        "model": "FIFO",
                        "remarks": "",
                    }
                    if pnl.empty:
                        pnl = pd.DataFrame([pnl_record])
                    else:
                        pnl = pd.concat(
                            [pnl, pd.DataFrame([pnl_record])], ignore_index=True
                        )

        if open_positions.empty:
            open_positions = open_trades
        else:
            open_positions = pd.concat([open_positions, open_trades], ignore_index=True)
        open_positions = open_positions[open_positions["quantity"] > 0]

    return pnl, open_positions
