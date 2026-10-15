import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "WASTESENSE API")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
API_V1_PREFIX = "/api/v1"
