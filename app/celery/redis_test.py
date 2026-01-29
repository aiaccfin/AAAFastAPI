import redis

# 通过 SSH 隧道访问
r = redis.Redis(host='localhost', port=8080, decode_responses=True)

try:
    pong = r.ping()
    print("Connected:", pong)
except Exception as e:
    print("Connection failed:", e)
