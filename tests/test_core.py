from service import check_point, escape_nickname, calc_sign, limit_page_size, parse_uid, rank_sort

# 测试 1：积分不足
def test_point_insufficient():
    assert check_point(10, 1000) == False

# 测试 2：积分足够
def test_point_sufficient():
    assert check_point(100, 50) == True

# 测试 3：积分刚好够
def test_point_exact():
    assert check_point(100, 100) == True

# 测试 4：XSS 转义
def test_xss_escape():
    escaped = escape_nickname("<script>alert(1)</script>")
    assert "<" not in escaped
    assert "&lt;" in escaped

# 测试 5：普通昵称不变
def test_normal_nickname():
    assert escape_nickname("张三") == "张三"

# 测试 6：签名计算一致性
def test_sign_consistent():
    sign1 = calc_sign(1, "PAID")
    sign2 = calc_sign(1, "PAID")
    assert sign1 == sign2

# 测试 7：不同参数签名不同
def test_sign_different():
    assert calc_sign(1, "PAID") != calc_sign(2, "PAID")

# 测试 8：page_size 上限
def test_page_size_limit():
    assert limit_page_size(999999) == 100
    assert limit_page_size(50) == 50

# 测试 9：token 解析
def test_parse_uid():
    assert parse_uid("601_1790673049") == 601

# 测试 10：同分排序（先达到的排前面）
def test_rank_same_score():
    data = [
        {"user_id": 602, "score": 100, "ts": 2},
        {"user_id": 603, "score": 100, "ts": 1},
    ]
    result = rank_sort(data)
    assert result[0]["user_id"] == 603  # ts 小的先达到，排前面

# 测试 11：不同分排序（分高的排前面）
def test_rank_different_score():
    data = [
        {"user_id": 601, "score": 50, "ts": 1},
        {"user_id": 602, "score": 100, "ts": 2},
    ]
    result = rank_sort(data)
    assert result[0]["user_id"] == 602  # 分数高的排前面