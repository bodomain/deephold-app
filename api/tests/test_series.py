"""Series API tests (require DB connection)."""

from fastapi.testclient import TestClient

from deephold_api.main import app

client = TestClient(app)


def test_list_series() -> None:
    response = client.get("/api/series?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5
    assert "id" in data[0]
    assert "type" in data[0]
    assert "name" in data[0]


def test_list_series_filter_type() -> None:
    response = client.get("/api/series?type=macro&limit=50")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(s["type"] == "macro" for s in data)


def test_list_series_search() -> None:
    response = client.get("/api/series?q=AAPL&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert any("AAPL" in s["identifier"] for s in data)


def test_get_series_detail() -> None:
    response = client.get("/api/series/macro:FRED:UNRATE")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "macro:FRED:UNRATE"
    assert data["type"] == "macro"
    assert data["count"] > 0


def test_get_series_not_found() -> None:
    response = client.get("/api/series/price:NONEXISTENT123")
    assert response.status_code == 404


def test_get_observations() -> None:
    response = client.get("/api/series/macro:FRED:UNRATE/observations?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5
    assert "date" in data[0]
    assert "value" in data[0]


def test_get_candles() -> None:
    response = client.get("/api/series/price:^GSPC/candles?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5
    assert "open" in data[0]
    assert "close" in data[0]


def test_get_candles_non_price() -> None:
    response = client.get("/api/series/macro:FRED:UNRATE/candles")
    assert response.status_code == 400


def test_get_stats() -> None:
    response = client.get("/api/series/price:^GSPC/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert data["latest"] is not None


def test_export_csv() -> None:
    response = client.get("/api/series/macro:FRED:UNRATE/export?format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "date,value" in response.text


def test_dashboard_macro() -> None:
    response = client.get("/api/dashboard/macro")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 9


def test_compare() -> None:
    response = client.post(
        "/api/compare",
        json={
            "ids": ["price:^GSPC", "price:^DJI"],
            "normalize": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["series"]) == 2
    assert len(data["dates"]) > 0


def test_correlation() -> None:
    response = client.post(
        "/api/correlation",
        json={
            "ids": ["price:^GSPC", "price:^DJI", "macro:FRED:VIXCLS"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["labels"]) == 3
    assert len(data["matrix"]) == 3
    assert len(data["matrix"][0]) == 3
