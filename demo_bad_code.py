import requests


def process_users(user_ids):
    results = []
    for uid in user_ids:
        user = db.query("SELECT * FROM users WHERE id=%s" % uid)  # 循环内逐条查询
        results.append(user)
    return results


API_KEY = "sk-live-abc123hardcodedsecret"  # 硬编码密钥


def fetch_data():
    try:
        return requests.get("https://api.example.com", headers={"k": API_KEY})
    except:
        pass
