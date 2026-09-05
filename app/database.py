from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import redis
# MySQL连接配置（需根据实际环境修改密码）
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/vending_system"
# 1. 初始化MySQL引擎与会话
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # 数据库模型基类
# 2. 初始化Redis客户端（默认配置，用于存储出货指令）
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
# 3. 依赖函数：为每个请求分配数据库会话，请求结束自动关闭
def get_db():
    db = SessionLocal()
    try:
        yield db  # 提供数据库会话给业务层
    finally:
        db.close()  # 确保会话关闭，避免连接泄露