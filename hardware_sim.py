import requests
import time

# 配置机器编号
MACHINE_CODE = "M001"
SERVER_URL = f"http://127.0.0.1:8000/hardware/{MACHINE_CODE}/poll"

print(f"🤖 售货机 [{MACHINE_CODE}] 启动成功！")
print(f"📡 正在连接服务器: {SERVER_URL}")
print("🕒 正在等待用户购买...\n")

try:
    while True:
        try:
            # 1. 向服务器询问：有我的指令吗？
            response = requests.get(SERVER_URL, timeout=5)
            data = response.json()

            # 2. 如果有指令
            if data.get("execute"):
                command = data["execute"]
                print(f"⚡ 收到指令: 【{command}】")
                print("⚙️  电机启动... 嗡嗡嗡...")
                time.sleep(2)  # 模拟出货耗时
                print("✅ 商品已掉落！")
                print("🕒 继续等待...\n")
            else:
                # 没有指令，打印一个点，表示活着
                print(".", end="", flush=True)

        except Exception as e:
            print(f"\n❌ 连接错误: {e}")

        # 3. 每隔 2 秒问一次 (省流量)
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🔌 机器已断电。")