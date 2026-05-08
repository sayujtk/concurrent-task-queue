def test_create_and_get_job(client):
    payload = {"type": "email", "payload": {"to": "user@example.com"}}
    resp = client.post("/jobs/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "email"
    assert data["payload"]["to"] == "user@example.com"

    job_id = data["id"]
    resp = client.get(f"/jobs/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == job_id


def test_list_jobs(client):
    for i in range(1000):
        client.post("/jobs/", json={"type": "bulk", "payload": {"i": i}})

    resp = client.get("/jobs/")
    assert resp.status_code == 200

    resp = client.get("/jobs/?limit=1000")
    data = resp.json()
    assert "jobs" in data
    assert len(data["jobs"]) == 1000


def test_stats(client):
    client.post("/jobs/", json={"type": "a", "payload": {"x": 1}})

    resp = client.get("/jobs/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "pending_count" in data
    assert data["pending_count"] >= 1