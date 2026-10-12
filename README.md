&#x20;vip-mini 靶子系统



&#x20;项目简介

一个用于测试练习的 FastAPI 靶子系统，包含 10 个接口，故意埋入 10 个已知缺陷，用于性能测试、安全扫描和自动化测试练习。



&#x20;技术栈

\- FastAPI + uvicorn

\- MySQL 8.0 (Docker)

\- Redis 7 (Docker)

\- DBUtils 连接池



&#x20;快速开始

bash

&#x20;1. 启动 Docker 容器

docker start projects-mysql-1 projects-redis-1

&#x20;2. 启动服务

uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

&#x20;3. 访问接口文档

http://127.0.0.1:8000/docs



性能测试

测试环境

CPU: i5-13420H (8核12线程)



内存: 16GB



压测工具: JMeter 5.6.3



优化前梯度数据

并发数	平均响应(ms)	P95(ms)	错误率	TPS

1	270	350	0%	3.7/sec

50	2640	4073	0%	14.53/sec

100	4895	7493	0%	16.42/sec

200	11102	19869	0%	11.81/sec

瓶颈定位

CPU 38%、内存 83%、磁盘读写低，无慢 SQL



瓶颈在 db.py 每次请求都新建 MySQL 连接



优化方案

引入 DBUtils 连接池，复用连接，最大连接数 20。



优化后数据

并发数	平均响应(ms)	P95(ms)	TPS

50	87.72	354	256.81/sec

100	39.00	76.95	397.14/sec

优化效果

100 并发下 TPS 从 16.42 提升到 397.14，提升约 24 倍

平均响应从 4895ms 降至 39ms



安全测试

使用 OWASP ZAP 做基线扫描，发现 6 条告警（均为 Swagger UI 通用问题）

手动验证并确认 10 个业务漏洞（SQL 注入、越权、XSS、支付伪造、积分负数等）

修复 5 个高危漏洞，复扫确认无新增风险



单元测试

11 个用例，覆盖率 100%

接入 GitHub Actions CI，覆盖率低于 70% 自动失败

