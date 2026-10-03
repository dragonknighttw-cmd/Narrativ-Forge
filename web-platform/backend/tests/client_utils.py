from fastapi import FastAPI
from fastapi.testclient import TestClient


def create_test_client(app: FastAPI) -> TestClient:
    return TestClient(app, base_url="http://localhost")
