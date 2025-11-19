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

    # print(user_id, broker)
    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        df["user_id"] = user_id
        df["broker"] = broker

        # df["quantity"] = np.where(
        #     df["trade_type"] == "buy", df["quantity"], -df["quantity"]
        # )

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

            update_pnl_fifo(user_id, broker, df)
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
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)

    pnl = update_pnl_fifo(user_id, "Zerodha", df)
    pnl = pnl.round(2)

    return JSONResponse(
        content={"status": "success", "data": pnl.to_dict(orient="records")},
        status_code=200,
    )


def update_pnl_fifo(user_id: str, broker: str, tradebook: pd.DataFrame):
    psql_engine = postgres_engine()
    unique_symbols = tradebook["symbol"].unique()

    # delete_stmt = """
    #     DELETE FROM fno_pnl WHERE user_id = %s AND broker = %s AND symbol = ANY(%s)
    # """
    # psql_engine.execute(delete_stmt, (user_id, broker, list(unique_symbols)))

    tradebook.sort_values(by=["trade_date", "order_execution_time"], inplace=True)

    pnl = pd.DataFrame(
        columns=[
            "user_id",
            "broker",
            "symbol",
            "exchange",
            "segment",
            "entry_date",
            "exit_date",
            "direction",
            "quantity",
            "lots",
            "lot_size",
            "buy_price",
            "sell_price",
            "buy_value",
            "sell_value",
            "gross_pnl",
            "charges",
            "net_pnl",
            "model",
            "remarks",
        ]
    )
    records = []
    open_positions = pd.DataFrame()
    for symbol in unique_symbols:
        tb = tradebook[tradebook["symbol"] == symbol]
        # how to copy a blank dataframe
        op = pd.DataFrame(columns=tb.columns.tolist())

        for index, trade in tb.iterrows():
            lookfor = "sell" if trade["trade_type"] == "buy" else "buy"
            ops = op[(op["trade_type"] == lookfor) & (op["quantity"] > 0)].sort_values(
                by=["order_execution_time"]
            )

            if ops.empty:
                op = pd.concat([op, pd.DataFrame([trade])], ignore_index=True)
            else:
                for o_index, open_trade in ops.iterrows():
                    if trade["quantity"] == 0:
                        break

                    qty = min(trade["quantity"], open_trade["quantity"])
                    trade["quantity"] -= qty
                    open_trade["quantity"] -= qty

                    pnl_record = {
                        "user_id": user_id,
                        "broker": broker,
                        "symbol": trade["symbol"],
                        "exchange": trade["exchange"],
                        "segment": trade["segment"],
                        "entry_date": (
                            open_trade["trade_date"]
                            if lookfor == "buy"
                            else trade["trade_date"]
                        ),
                        "exit_date": (
                            trade["trade_date"]
                            if lookfor == "buy"
                            else open_trade["trade_date"]
                        ),
                        "direction": "long" if lookfor == "buy" else "short",
                        "quantity": qty,
                        "lots": 1,
                        "lot_size": qty,
                        "buy_price": (
                            open_trade["price"] if lookfor == "buy" else trade["price"]
                        ),
                        "sell_price": (
                            trade["price"] if lookfor == "buy" else open_trade["price"]
                        ),
                        "buy_value": qty
                        * (open_trade["price"] if lookfor == "buy" else trade["price"]),
                        "sell_value": qty
                        * (trade["price"] if lookfor == "buy" else open_trade["price"]),
                        "gross_pnl": qty
                        * (
                            (trade["price"] - open_trade["price"])
                            if lookfor == "buy"
                            else (open_trade["price"] - trade["price"])
                        ),
                        "charges": 0.0,
                        "net_pnl": 0.0,
                        "model": "FIFO",
                        "remarks": "",
                    }
                    pnl = pd.concat(
                        [pnl, pd.DataFrame([pnl_record])], ignore_index=True
                    )
        open_positions = pd.concat([open_positions, ops], ignore_index=True)
    print(open_positions)
    open_positions.to_clipboard()
    return pnl
