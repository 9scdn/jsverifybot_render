import json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


def load_config():
    return config


def is_official_account(username: str) -> bool:
    """
    判断给定用户名是否在官方账号列表中（支持大小写混合）
    """
    username = username.lower().strip()
    official_list = [a.lower() for a in config.get("official_accounts", [])]
    public_list = [a.lower() for a in config.get("public_accounts", [])]
    return username in official_list or username in public_list
