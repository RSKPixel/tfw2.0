from kiteconnect import KiteConnect
import requests
import sqlalchemy
from urllib.parse import quote_plus
from os import path


# Kite API Configuration
KITE_API_KEY = "tw96psyyds0yj8vj"
KITE_API_SECRET = "3iewov9onkbytzramkt263r9lvcdzks9"
ACCESS_TOKEN_API_URL = "http://kite.trialnerror.in/accesstoken/"

# Database Configuration
DB_HOST = "tfw.trialnerror.in"
DB_PORT = 5432
DB_USER = "sysadmin"
DB_PASSWORD = quote_plus("Apple@1239")
DB_NAME = "tfw"

# Base Directory
BASE_DIR = path.dirname(path.abspath(__file__))
DATA_DIR = path.join(BASE_DIR, "data")


# Function to create and return a PostgreSQL engine
def postgres_engine() -> sqlalchemy.engine.Engine:
    try:
        DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = sqlalchemy.create_engine(DATABASE_URL)
    except Exception as e:
        print("Error creating database engine:", e)
        return None
    return engine


# Function to connect to Kite API
def kite_connect() -> KiteConnect:
    api_key = KITE_API_KEY
    api_secret = KITE_API_SECRET
    access_token_api_url = ACCESS_TOKEN_API_URL

    request = requests.get(access_token_api_url)
    access_token = request.json().get("access_token", "")

    kite = KiteConnect(api_key=api_key)
    try:
        kite.set_access_token(access_token)
        profile = kite.profile()
    except Exception as e:
        print("Error setting access token:", e)

        loginurl = kite.login_url()
        kite = None
        print("Login URL:", loginurl)
        return None

    return kite
