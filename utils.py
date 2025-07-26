import json

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def is_official_account(username):
    config = load_config()
    return username.lower() in [u.lower() for u in config["official_accounts"]]
