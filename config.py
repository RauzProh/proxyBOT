import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


API_TOKEN = os.getenv("API_TOKEN")
PX6_API_KEY = os.getenv("PX6_API_KEY")

YK_account_id = os.getenv("YK_account_id")
YK_secret_key = os.getenv("YK_secret_key")