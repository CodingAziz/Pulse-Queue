def test_create_job(client):
    response = client.post(
        "/jobs/",
        json={
            "type": "email",
            "payload": {"to": "test@example.com"}
        },
        headers={"X-Client-ID": "test-client"}
    )

    assert response.status_code == 201
    assert "id" in response.json