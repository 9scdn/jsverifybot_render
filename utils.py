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


def is_official_email(email: str) -> bool:
    """
    判断给定邮箱是否在官方邮箱列表中（支持大小写混合）
    """
    email = email.lower().strip()
    official_emails = [e.lower() for e in config.get("official_emails", [])]
    return email in official_emails
