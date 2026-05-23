def test_homepage_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_login_regist_page_returns_200(client):
    response = client.get("/login_regist")
    assert response.status_code == 200


def test_overview_page_returns_200(client):
    response = client.get("/overview")
    assert response.status_code == 200


def test_note_page_returns_200(client):
    response = client.get("/note/sample-note-id")
    assert response.status_code == 200
