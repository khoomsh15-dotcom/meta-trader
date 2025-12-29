import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client['TradingBotDB']
users_col = db['users']

def get_user(user_id):
    return users_col.find_one({"user_id": user_id})

def save_creds(user_id, login, password, server):
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"mt5_id": login, "mt5_pass": password, "mt5_server": server}},
        upsert=True
    )

def update_trade_settings(user_id, asset, lot, streak):
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"active_asset": asset, "base_lot": lot, "max_streak": streak, "is_running": True}}
    )
