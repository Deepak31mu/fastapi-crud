"""Integration tests for the /api/v1/users endpoints."""


# ── CREATE ───────────────────────────────────────────────────────────────────


class TestCreateUser:
    async def test_create_user_success(self, async_client, sample_user_payload):
        resp = await async_client.post("/api/v1/users/", json=sample_user_payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == sample_user_payload["name"]
        assert body["email"] == sample_user_payload["email"]
        assert body["is_active"] is True
        assert "_id" in body

    async def test_create_user_duplicate_email(
        self, async_client, created_user, sample_user_payload
    ):
        resp = await async_client.post("/api/v1/users/", json=sample_user_payload)
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    async def test_create_user_invalid_email(self, async_client):
        resp = await async_client.post(
            "/api/v1/users/", json={"name": "Bad", "email": "not-an-email"}
        )
        assert resp.status_code == 422

    async def test_create_user_missing_name(self, async_client):
        resp = await async_client.post(
            "/api/v1/users/", json={"email": "valid@example.com"}
        )
        assert resp.status_code == 422


# ── READ ─────────────────────────────────────────────────────────────────────


class TestGetUser:
    async def test_get_user_success(self, async_client, created_user):
        user_id = created_user["_id"]
        resp = await async_client.get(f"/api/v1/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["_id"] == user_id

    async def test_get_user_not_found(self, async_client, mock_db):
        resp = await async_client.get("/api/v1/users/507f1f77bcf86cd799439011")
        assert resp.status_code == 404


class TestListUsers:
    async def test_list_users_empty(self, async_client, mock_db):
        resp = await async_client.get("/api/v1/users/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["users"] == []

    async def test_list_users_with_data(self, async_client, created_user):
        resp = await async_client.get("/api/v1/users/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1
        assert len(body["users"]) >= 1

    async def test_list_users_pagination(self, async_client, mock_db):
        for i in range(3):
            await async_client.post(
                "/api/v1/users/",
                json={"name": f"User {i}", "email": f"user{i}@example.com"},
            )
        resp = await async_client.get("/api/v1/users/?page=1&page_size=2")
        body = resp.json()
        assert body["total"] == 3
        assert len(body["users"]) == 2
        assert body["page"] == 1
        assert body["page_size"] == 2


# ── UPDATE ───────────────────────────────────────────────────────────────────


class TestUpdateUser:
    async def test_update_user_name(self, async_client, created_user):
        user_id = created_user["_id"]
        resp = await async_client.patch(
            f"/api/v1/users/{user_id}", json={"name": "Updated Name"}
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    async def test_update_user_not_found(self, async_client, mock_db):
        resp = await async_client.patch(
            "/api/v1/users/507f1f77bcf86cd799439011", json={"name": "Ghost"}
        )
        assert resp.status_code == 404

    async def test_update_user_duplicate_email(self, async_client, mock_db):
        await async_client.post(
            "/api/v1/users/", json={"name": "User A", "email": "a@example.com"}
        )
        r2 = await async_client.post(
            "/api/v1/users/", json={"name": "User B", "email": "b@example.com"}
        )
        user_b_id = r2.json()["_id"]
        resp = await async_client.patch(
            f"/api/v1/users/{user_b_id}", json={"email": "a@example.com"}
        )
        assert resp.status_code == 409


# ── DELETE ───────────────────────────────────────────────────────────────────


class TestDeleteUser:
    async def test_delete_user_success(self, async_client, created_user):
        user_id = created_user["_id"]
        resp = await async_client.delete(f"/api/v1/users/{user_id}")
        assert resp.status_code == 204

        resp = await async_client.get(f"/api/v1/users/{user_id}")
        assert resp.status_code == 404

    async def test_delete_user_not_found(self, async_client, mock_db):
        resp = await async_client.delete("/api/v1/users/507f1f77bcf86cd799439011")
        assert resp.status_code == 404


# ── HEALTH ───────────────────────────────────────────────────────────────────


class TestHealthCheck:
    async def test_health(self, async_client, mock_db):
        resp = await async_client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "database" in body
        assert body["app"] == "fastapi-crud"
