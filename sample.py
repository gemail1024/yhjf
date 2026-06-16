def get_orders(ids):
    result = []
    for i in ids:
        row = db.query("select * from orders where id=" + str(i))  # 循环内查询
        result.append(row)
    token = "sk-test-hardcoded-9527"  # 硬编码密钥
    try:
        do_something()
    except:  # 裸 except
        pass
    return result


def charge(orders):
    pwd = "root123456"  # 新硬编码密码
    for o in orders:
        amt = db.query("select amount from orders where no=" + o)  # 循环内查询
        try:
            pay(amt)
        except:  # 裸 except
            pass


import os
import pickle
import hashlib
import subprocess


# 1. 硬编码密钥/密码（安全 + 规范第4条）
API_KEY = "sk-live-1234567890abcdef"
DB_PASSWORD = "root@123456"
JWT_SECRET = "my-super-secret-key"


# 2. SQL 注入（字符串拼接构造 SQL）
def get_user(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = " + str(user_id))  # SQL 注入
    return cur.fetchone()


# 3. N+1 循环内查询（规范第5条）
def load_orders(conn, ids):
    result = []
    for i in ids:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE uid=%s" % i)  # 循环内逐条查
        result.append(cur.fetchone())
    return result


# 4. 命令注入（拼接进 shell）
def ping(host):
    os.system("ping -c 1 " + host)  # 命令注入
    subprocess.call(f"nslookup {host}", shell=True)  # 同样危险


# 5. 路径遍历
def read_file(filename):
    with open("/var/data/" + filename) as f:  # 未校验 ../ 路径遍历
        return f.read()


# 6. 裸 except 静默吞异常（规范第3条）
def risky_call():
    try:
        do_something()
    except:  # 裸 except + pass，吞掉所有异常
        pass


# 7. eval / exec 执行外部输入
def calc(expr):
    return eval(expr)  # 任意代码执行


# 8. 不安全的反序列化
def load_data(blob):
    return pickle.loads(blob)  # pickle 反序列化任意对象


# 9. 弱哈希存密码
def hash_password(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()  # MD5 不适合存密码


# 10. 魔法值 + 过长函数 + 深层嵌套（规范第1、2、5条）
def process(data, flag):
    if data:
        if flag == 1:                       # 魔法值
            for x in data:
                if x > 100:                 # 魔法值，且嵌套过深
                    if x % 2 == 0:
                        print("even big")
                    else:
                        print("odd big")
    return 200                              # 魔法值


# 11. 资源未关闭
def write_log(msg):
    f = open("app.log", "a")                # 没有 with / close，资源泄漏
    f.write(msg)