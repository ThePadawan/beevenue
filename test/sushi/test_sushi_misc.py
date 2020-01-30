from sashimmie import sashimmie


def test_sushi_none_saved(adminClient, monkeypatch):
    def mock_get_saved(config):
        return []
    monkeypatch.setattr(sashimmie, "get_saved", mock_get_saved)

    r = adminClient.post("/sushi/next")
    assert r.status_code == 200
    assert "newIds" in r.json
    assert len(r.json["newIds"]) == 0


def test_sushi_two_saved(adminClient, monkeypatch):
    with open("test/resources/medium_to_be_uploaded.png", 'rb') as f:
        medium_bytes = f.read()

    def mock_get_saved(config):
        return [
            ("id0", [("", medium_bytes, "medium0.png")]),
            ("id1", [("", medium_bytes, "medium0.png")]),
        ]

    acknowledged_ids = set()

    def mock_ack(id):
        acknowledged_ids.add(id)

    monkeypatch.setattr(sashimmie, "get_saved", mock_get_saved)
    monkeypatch.setattr(sashimmie, "acknowledge", mock_ack)

    r = adminClient.post("/sushi/next")

    assert r.status_code == 200
    assert "newIds" in r.json
    assert len(r.json["newIds"]) == 1
    assert r.json["status"] == "continue"

    assert len(acknowledged_ids) == 1
    assert "id0" in acknowledged_ids
    assert "id1" not in acknowledged_ids
