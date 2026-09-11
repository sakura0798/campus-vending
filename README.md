
# 校园自动售货机

功能：学生在页面上选商品下单，付钱自动找零；后台能看库存和销售总额，点一下补货就把商品补上；下单成功后往 Redis 写一条出货指令，配套的小脚本轮询取走指令，模拟售货机出货。

后端 FastAPI + SQLAlchemy，数据库 MySQL，缓存用的 Redis，页面用 Jinja2。测试用 pytest，测试里把 MySQL 和 Redis 都 mock 掉了，不起数据库也能跑。

## 目录

```
campus_vending/
├── app/                  后端代码
│   ├── main.py           路由和业务逻辑都在这
│   ├── database.py       数据库连接、Redis、get_db 依赖
│   └── templates/        index（购买端）和 admin（管理端）两个页面
├── tests/                测试
│   ├── conftest.py       主要做 mock：Redis 和 get_db
│   └── test_api.py       购买、补货、轮询的用例
├── init_db.py            初始化数据库 + 种子商品
├── hardware_sim.py       售货机硬件模拟器
└── requirements.txt
```

需要 Python 3.10+，装了 MySQL 和 Redis。

1. 装依赖

   ```
   pip install -r requirements.txt
   ```

2. 初始化数据库（会重新建 vending_system 库，塞 6 种商品）

   ```
   python init_db.py
   ```

   连接信息在 app/database.py，密码和你的不一致就改这里。

3. 启动

   ```
   uvicorn app.main:app --port 8000
   ```

   - http://127.0.0.1:8000/      买东西的页面
   - http://127.0.0.1:8000/admin  管理页面

4. （可选）另开一个终端跑硬件模拟器，能看到出货指令

   ```
   python hardware_sim.py
   ```

5. 跑测试

   ```
   python -m pytest tests/ -v
   ```


| 方法   | 路径                    | 说明                |
|------|-----------------------|-------------------|
| GET  | /                     | 购买端首页             |
| GET  | /admin                | 管理端               |
| POST | /api/buy              | 下单（扣库存、算找零、写出货指令） |
| POST | /api/refill           | 补货                |
| GET  | /hardware/{code}/poll | 硬件轮询，取出货指令        |

## 坑

- .venv 在中文路径下创建容易坏，报 Fatal error 时用 python -m pytest 或者重装一次就解决
- 测 FastAPI 时 patch("app.main.get_db") 不生效，得用 app.dependency_overrides 换依赖

