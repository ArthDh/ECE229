def test_index(app, client):
    res = client.get('/')
    assert res.status_code == 200
    # expected = {'hello': 'world'}
    # assert expected == json.loads(res.get_data(as_text=True))

def test_signout(app, client):
    res = client.get('/sign_out')
    assert res.status_code == 302

def test_docs(app, client):
    res = client.get('/docs')
    assert res.status_code == 302

def test_dash(app, client):
    res = client.get('/dashboard')
    assert res.status_code == 308