import json


def test_index(app, client):
    res = client.get('/')
    assert res.status_code == 200
    expected = {"status": "Success"}
    assert expected == json.loads(res.get_data(as_text=True))


def test_types(app, client):
    res = client.get('/element_types')
    assert res.status_code == 200


def test_search(app, client):
    res = client.get('/search_players')
    assert res.status_code == 200
