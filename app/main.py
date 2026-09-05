from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DECIMAL, Text, DateTime, func
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import uuid
import json
from datetime import datetime
from app.database import Base, engine, get_db, redis_client


# --- 模型定义 ---
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(DECIMAL(10, 2))
    image = Column(String(50))
    stock = Column(Integer)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_no = Column(String(50))
    total_amount = Column(DECIMAL(10, 2))
    paid_amount = Column(DECIMAL(10, 2))
    change_amount = Column(DECIMAL(10, 2))
    items_detail = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


# --- 请求数据格式 ---
class PurchaseItem(BaseModel):
    product_id: int
    count: int


class PurchaseRequest(BaseModel):
    items: list[PurchaseItem]
    paid_amount: float


class RefillRequest(BaseModel):
    product_id: int
    amount: int = 20


# --- 1. 首页：学生购买端 ---
@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return templates.TemplateResponse("index.html", {"request": request, "products": products})


# --- 2. 后台：运营管理端 (修复了这里！) ---
@app.get("/admin")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    # 获取所有商品(包含库存信息)
    machines = db.query(Product).all()
    # 计算总销售额
    total_sales = db.query(func.sum(Order.total_amount)).scalar() or 0

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "machines": machines,
        "total_sales": round(total_sales, 2)
    })


# --- 3. 接口：购买结算 ---
@app.post("/api/buy")
def buy_products(req: PurchaseRequest, db: Session = Depends(get_db)):
    total_cost = 0
    bought_names = []

    # 计算检查
    for item in req.items:
        if item.count <= 0: continue
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product: raise HTTPException(404, "商品不存在")
        if product.stock < item.count: raise HTTPException(400, f"{product.name} 库存不足")

        total_cost += float(product.price) * item.count
        bought_names.append(f"{product.name}x{item.count}")

    if req.paid_amount < total_cost:
        raise HTTPException(400, "金额不足")

    # 扣库存
    for item in req.items:
        if item.count <= 0: continue
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock -= item.count

    # 记账
    new_order = Order(
        order_no=str(uuid.uuid4())[:8],
        total_amount=total_cost,
        paid_amount=req.paid_amount,
        change_amount=req.paid_amount - total_cost,
        items_detail=json.dumps(bought_names, ensure_ascii=False)
    )
    db.add(new_order)
    db.commit()

    # 发指令
    cmd_str = f"Dispense: {', '.join(bought_names)}"
    redis_client.set("cmd:M001", cmd_str, ex=60)

    return {"msg": "购买成功", "change": new_order.change_amount, "order_no": new_order.order_no}


# --- 4. 接口：一键补货 (刚才加的功能) ---
@app.post("/api/refill")
def refill_stock(req: RefillRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product: raise HTTPException(404, "商品不存在")

    product.stock = req.amount
    db.commit()
    return {"msg": f"【{product.name}】补货完成", "stock": product.stock}


# --- 5. 接口：硬件轮询 ---
@app.get("/hardware/{code}/poll")
def poll(code: str):
    cmd = redis_client.get(f"cmd:{code}")
    if cmd:
        redis_client.delete(f"cmd:{code}")
        return {"execute": cmd}
    return {"execute": None}