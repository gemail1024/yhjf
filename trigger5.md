# 规范检查验证

时间:16:22:43

```python
def process(items):
    try:
        for i in items:
            data = db.query(i)  # 循环内查询
            api_key = 'sk-hardcoded-123456'  # 硬编码密钥
            print(data)
    except:
        pass
```
