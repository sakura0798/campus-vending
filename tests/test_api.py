from unittest.mock import MagicMock


class TestBuyAPI:
    def test_buy_success(self, client, mock_db):
        product = type("Product", (), {"id": 1, "name": "可乐", "price": 3.00, "stock": 100})()
        mock_db.query.return_value.filter.return_value.first.return_value = product

        resp = client.post("/api/buy", json={"items": [{"product_id": 1, "count": 1}], "paid_amount": 5.0})
        assert resp.status_code == 200
        assert resp.json()["msg"] == "购买成功"

    def test_buy_stock_not_enough(self, client, mock_db):
        product = type("Product", (), {"id": 1, "name": "可乐", "price": 3.00, "stock": 2})()
        mock_db.query.return_value.filter.return_value.first.return_value = product

        resp = client.post("/api/buy", json={"items": [{"product_id": 1, "count": 5}], "paid_amount": 50.0})
        assert resp.status_code == 400
        assert "库存不足" in resp.json()["detail"]

    def test_buy_amount_not_enough(self, client, mock_db):
        product = type("Product", (), {"id": 1, "name": "可乐", "price": 10.00, "stock": 100})()
        mock_db.query.return_value.filter.return_value.first.return_value = product

        resp = client.post("/api/buy", json={"items": [{"product_id": 1, "count": 1}], "paid_amount": 1.0})
        assert resp.status_code == 400
        assert "金额不足" in resp.json()["detail"]


class TestRefillAPI:
    def test_refill_success(self, client, mock_db):
        product = type("Product", (), {"id": 1, "name": "可乐", "price": 3.00, "stock": 10})()
        mock_db.query.return_value.filter.return_value.first.return_value = product

        resp = client.post("/api/refill", json={"product_id": 1, "amount": 50})
        assert resp.status_code == 200
        assert "补货完成" in resp.json()["msg"]

    def test_refill_product_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resp = client.post("/api/refill", json={"product_id": 999, "amount": 20})
        assert resp.status_code == 404
        assert "商品不存在" in resp.json()["detail"]


class TestPollAPI:
    def test_poll_no_command(self, client):
        resp = client.get("/hardware/M001/poll")
        assert resp.status_code == 200
        assert resp.json()["execute"] is None

    def test_poll_has_command(self, client, mock_redis):
        mock_redis.get.return_value = "Dispense: 可乐"
        resp = client.get("/hardware/M001/poll")
        assert resp.status_code == 200
        assert resp.json()["execute"] == "Dispense: 可乐"
