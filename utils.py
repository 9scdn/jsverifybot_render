import json

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

def is_official_account(username: str) -> bool:
    username = username.lower()
    return (
        username in [a.lower() for a in config.get("official_accounts", [])] or
        username in [a.lower() for a in config.get("public_accounts", [])]
    )
