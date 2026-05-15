import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app


@pytest.mark.asyncio
async def test_request_without_api_key_returns_401():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/cart/user_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_request_with_wrong_api_key_returns_401():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/cart/user_123",
            headers={"X-API-Key": "wrong-key"}
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_request_with_correct_api_key_passes_auth(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key-123")
    with patch("app.controllers.cart_controller.cart_service") as mock_svc:
        mock_svc.get_cart = AsyncMock(return_value={
            "user_id": "user_123", "items": {}, "total_items": 0
        })
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/cart/user_123",
                headers={"X-API-Key": "test-key-123"}
            )
    # 404 porque el carrito está vacío — pero la autenticación pasó
    assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_health_endpoint_does_not_require_api_key():
    """El /health debe ser público para los health checks de Railway."""
    with patch("app.main.get_redis") as mock_get:
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_get.return_value = mock_redis
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")
    assert response.status_code == 200