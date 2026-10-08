from fastapi import FastAPI
from fastapi.testclient import TestClient


def create_test_client(app: FastAPI) -> TestClient:
    # Keep app-level rate-limit state isolated between test clients.
    rate_windows = getattr(__import__("app.main", fromlist=["_rate_windows"]), "_rate_windows", None)
    if rate_windows is not None:
        rate_windows.clear()
    return TestClient(app, base_url="http://localhost")
