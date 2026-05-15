import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app


MOCK_CART_DATA = {f"prod_{i:03d}": str(i) for i in range(1, 11)}  # 10 productos
HEADERS = {"X-API-Key": "test-key"}


@pytest.mark.asyncio
async def test_get_cart_without_pagination_returns_all_items(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    with patch("app.services.cart_service.cart_repository") as mock_repo:
        mock_repo.get_cart = AsyncMock(return_value=MOCK_CART_DATA)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/cart/user_123", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 10
        assert data["page"] == 1
        assert data["total_pages"] == 1
        assert len(data["items"]) == 10


@pytest.mark.asyncio
async def test_get_cart_with_pagination_returns_first_page(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    with patch("app.services.cart_service.cart_repository") as mock_repo:
        mock_repo.get_cart = AsyncMock(return_value=MOCK_CART_DATA)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/cart/user_123?page=1&page_size=3", headers=HEADERS
            )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total_items"] == 10
        assert data["total_pages"] == 4
        assert data["page"] == 1


@pytest.mark.asyncio
async def test_get_cart_with_pagination_returns_last_page(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    with patch("app.services.cart_service.cart_repository") as mock_repo:
        mock_repo.get_cart = AsyncMock(return_value=MOCK_CART_DATA)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/cart/user_123?page=4&page_size=3", headers=HEADERS
            )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1  # última página tiene 1 ítem
        assert data["page"] == 4


@pytest.mark.asyncio
async def test_get_cart_page_beyond_total_returns_empty_items(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    with patch("app.services.cart_service.cart_repository") as mock_repo:
        mock_repo.get_cart = AsyncMock(return_value=MOCK_CART_DATA)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/cart/user_123?page=99&page_size=3", headers=HEADERS
            )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == {}
