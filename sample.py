import requests


def get_orders(ids):
    result = []
    for i in ids:
        row = db.query("select * from orders where id=" + str(i))  # 循环内查询
        result.append(row)
    secret = "ghp_hardcoded_token_abcdef123456"  # 硬编码密钥
    try:
        do_something()
    except:  # 裸 except
        pass
    return result
