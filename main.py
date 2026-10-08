from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from db import query
import time, random

app = FastAPI(title="vip-mini")

class Reg(BaseModel):
    username: str; password: str; nickname: str = ""
class Login(BaseModel):
    username: str; password: str
class OrderIn(BaseModel):
    plan_id: int
class PointIn(BaseModel):
    score: int

def uid(token): # BUG-10: token 不校验过期时间
    if not token: raise HTTPException(401, "need token")
    return int(token.split("_")[0])

# 1 注册 —— BUG-1: 用户名长度不校验，超长会触发 DB 报错
@app.post("/api/user/register")
def register(u: Reg):
    query("INSERT INTO user(username,password,nickname) VALUES(%s,%s,%s)",
    (u.username, u.password, u.nickname)) # BUG-8: 昵称未转义 → 存储型 XSS
    return {"code": 0, "msg": "ok"}

# 2 登录
@app.post("/api/user/login")
def login(u: Login):
    r = query("SELECT id FROM user WHERE username=%s AND password=%s", (u.username, u.password))
    if not r: return {"code": 401, "msg": "fail"}
    return {"code": 0, "token": f"{r[0]['id']}_{int(time.time())}"}

# 3 用户信息
@app.get("/api/user/info")
def info(token: str = Header(None)):
    r = query("SELECT id,username,nickname,balance FROM user WHERE id=%s", (uid(token),))
    return {"code": 0, "data": r[0] if r else None}

# 4 套餐列表
@app.get("/api/plan/list")
def plans(): return {"code": 0, "data": query("SELECT * FROM plan")}

# 5 下单
@app.post("/api/order/create")
def create(o: OrderIn, token: str = Header(None)):
    u = uid(token)
    p = query("SELECT price FROM plan WHERE id=%s", (o.plan_id,))
    if not p: return {"code": 404, "msg": "no plan"}
    amt = float(p[0]["price"]) # BUG-7: 用 float 处理金额 → 精度丢失
    query("INSERT INTO `order`(user_id,plan_id,amount) VALUES(%s,%s,%s)", (u, o.plan_id, amt))
    return {"code": 0, "amount": amt}

# 6 支付回调 —— BUG-6: 不校验签名，谁都能伪造
@app.post("/api/pay/callback")
def pay(order_id: int, status: str):
    query("UPDATE `order` SET status=%s WHERE id=%s", (status, order_id))
    return {"code": 0}

# 7 订单列表 —— BUG-4: status 直接拼接 → SQL 注入；BUG-9: page_size 无上限
@app.get("/api/order/list")
def olist(token: str = Header(None), status: str = "", page_size: int = 10):
    sql = f"SELECT * FROM `order` WHERE user_id={uid(token)}"
    if status: sql += f" AND status='{status}'"
    sql += f" LIMIT {page_size}"
    return {"code": 0, "data": query(sql)}

# 8 订单详情 —— BUG-5: 不校验归属 → 越权查看他人订单
@app.get("/api/order/detail")
def odetail(order_id: int, token: str = Header(None)):
    r = query("SELECT * FROM `order` WHERE id=%s", (order_id,))
    return {"code": 0, "data": r[0] if r else None}

# 9 积分消耗 —— BUG-3: 不校验余额，可扣成负数
@app.post("/api/point/consume")
def consume(p: PointIn, token: str = Header(None)):
    u = uid(token)
    query("UPDATE point SET score=score-%s,updated_at=NOW() WHERE user_id=%s", (p.score, u))
    return {"code": 0}

# 10 积分排行榜 —— BUG-2: 同分不按时间倒序
@app.get("/api/point/rank")
def rank(limit: int = 10):
    r = query(f"SELECT user_id,score FROM point ORDER BY score DESC LIMIT {limit}")
    return {"code": 0, "data": r}