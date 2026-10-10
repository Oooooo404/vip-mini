import html
import hashlib
from decimal import Decimal

def check_point(current_score,consume_score):
    """检查积分是否足够，返回True/False"""
    return current_score >= consume_score

def escape_nickname(nickname):
    """转义昵称，防止XSS"""
    return html.escape(nickname)

def calc_sign(order_id,status,secret="vip-mini-secret"):
    """计算支付签名"""
    return hashlib.md5(f"{order_id}{status}{secret}".encode()).hexdigest()

def limit_page_size(page_size,max_size=100):
    """限制page_size上限"""
    return min(page_size,max_size)

def parse_uid(token):
    """从token解析用户id"""
    return int(token.split("_")[0])

def rank_sort(data):
    """按分数降序、时间升序排序（同分时先达到的排前面）"""
    return sorted(data,key=lambda x: (-x["score"],x["ts"]))