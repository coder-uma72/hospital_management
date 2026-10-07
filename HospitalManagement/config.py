import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        database=os.getenv("MYSQL_DATABASE")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]

    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False

    JWT_TOKEN_LOCATION = ["headers", "cookies"]

    JWT_COOKIE_SECURE = False

    JWT_COOKIE_CSRF_PROTECT = False

