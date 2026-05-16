"""Нагрузочный сценарий для Device Stats Service.

Запуск (web UI):
    locust -f locustfile.py --host http://localhost:8000

Запуск (headless):
    locust -f locustfile.py --host http://localhost:8000 \
        --headless -u 50 -r 10 -t 1m
"""
import random
import uuid

from locust import HttpUser, between, task


class DeviceStatsUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        # Каждый виртуальный пользователь создаёт собственного user'а и устройство,
        # чтобы нагрузка распределялась равномерно по разным записям БД.
        user_resp = self.client.post(
            "/users",
            json={"name": f"loadtest-{uuid.uuid4().hex[:8]}"},
            name="setup: POST /users",
        )
        self.user_id = user_resp.json()["id"]

        device_resp = self.client.post(
            "/devices",
            json={"name": f"sensor-{uuid.uuid4().hex[:8]}", "user_id": self.user_id},
            name="setup: POST /devices",
        )
        self.device_id = device_resp.json()["id"]

    @task(5)
    def post_reading(self) -> None:
        self.client.post(
            f"/devices/{self.device_id}/readings",
            json={
                "x": random.uniform(-100, 100),
                "y": random.uniform(-100, 100),
                "z": random.uniform(-100, 100),
            },
            name="POST /devices/:id/readings",
        )

    @task(2)
    def get_device_stats(self) -> None:
        self.client.get(
            f"/devices/{self.device_id}/stats",
            name="GET /devices/:id/stats",
        )

    @task(1)
    def get_user_stats(self) -> None:
        self.client.get(
            f"/users/{self.user_id}/stats",
            name="GET /users/:id/stats",
        )
