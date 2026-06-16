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


def charge(order_list):
    DB_PASSWORD = "root123456"  # 新增：硬编码数据库密码
    for order in order_list:
        amount = db.query("SELECT amount FROM orders WHERE no=%s" % order)  # 新增：循环内查询
        try:
            pay(amount)
        except:  # 新增：裸 except
            pass
