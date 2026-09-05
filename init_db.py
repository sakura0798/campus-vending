import pymysql
# 数据库配置
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "vending_system"
def init_database():
    # 连接MySQL服务器（未指定数据库）
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    print("🔄 正在重置数据库...")
    # 1. 重建数据库（删除旧库避免结构冲突）
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4")
    cursor.execute(f"USE {DB_NAME}")
    # 2. 创建商品表
    cursor.execute("""
    CREATE TABLE products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        price DECIMAL(10, 2),
        image VARCHAR(50),
        stock INT DEFAULT 20
    )
    """)
    # 3. 创建订单表
    cursor.execute("""
    CREATE TABLE orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_no VARCHAR(50),
        total_amount DECIMAL(10, 2),
        paid_amount DECIMAL(10, 2),
        change_amount DECIMAL(10, 2),
        items_detail TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # 4. 初始化6种商品数据（校园热门品类）
    products = [
        ('可口可乐', 3.00, '🥤', 20),
        ('百事雪碧', 3.00, '🟢', 20),
        ('矿泉水', 2.00, '💧', 50),
        ('鲜橙多', 4.50, '🍊', 15),
        ('原味薯片', 6.00, '🥔', 10),
        ('奥利奥', 5.50, '🍪', 12)
    ]
    cursor.executemany(
        "INSERT INTO products (name, price, image, stock) VALUES (%s, %s, %s, %s)",
        products
    )
    conn.commit()
    conn.close()
    print("✅ 数据库升级完成！已载入6种商品。")
if __name__ == "__main__":
    init_database()