import os
import tempfile
from app import create_app
import pytest

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()

    config = {
        "api_version": 2,
        "outdir": "test",
        "database_path": db_path,
    }
    os.system(f"sqlite3 {db_path} < createdb.sql")
    os.system(f"sqlite3 {db_path} < testsetup.sql")

    app = create_app(config)

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def test_new_session(client):

    valid_user_id = "c6354001bc5d6538dd856d00aa25a2458e44fd3b9214d4bad2dc06278f6b059f"
    invalid_user_id = "6577cf1647ebe16f66facd1c83af5ab388a23470de8460873732cad5b32afcc8"

    # request for user that does not exist -- expecting 401
    resp = client.get(f"/sessions/{invalid_user_id}/new")
    assert resp.status_code == 401

    # requesting session for user w/o active session -- expecting 200 + new session id
    resp = client.get(f"/sessions/{valid_user_id}/new")
    assert resp.status_code == 200
    
    obj = resp.json
    assert isinstance(obj, dict)
    assert len(obj.get("session_id")) == 64
    assert obj.get("status") == "OK"

    sess_id = obj["session_id"]

    # requesting session for user w/ existing session -- expecting 200 + previously 
    # received session id (sess_id)
    resp = client.get(f"/sessions/{valid_user_id}/new")
    assert resp.status_code == 200
    
    obj = resp.json
    assert isinstance(obj, dict)
    assert len(obj.get("session_id")) == 64
    assert obj.get("status") == "OK"
    assert obj.get("session_id") == sess_id # check with previous session_id

def test_close_session(client):
    valid_user_id = "c6354001bc5d6538dd856d00aa25a2458e44fd3b9214d4bad2dc06278f6b059f"
    invalid_session_id = "wront-session-id"

    # requesting session for user w/o active session -- expecting 200 + new session id
    resp = client.get(f"/sessions/{valid_user_id}/new")
    assert resp.status_code == 200
    obj = resp.json
    sess_id = obj["session_id"] # extract current session id

    # close the current session id
    resp = client.get(f"/sessions/{sess_id}/close")
    assert resp.status_code == 200 # /close will always return 200!

    # requesting session for user w/ existing session -- expecting 200 + new session id 
    # (since we closed the previous one)
    resp = client.get(f"/sessions/{valid_user_id}/new")
    assert resp.status_code == 200
    
    obj = resp.json
    assert isinstance(obj, dict)
    assert obj.get("session_id") != sess_id # make sure we get a new one!

    # try an invalid session id. 
    # NOTE: the API will fail silently, still returning 200
    # even for invalid session ids. This might change in the future.
    # If that's the case, this test will need to be changed (e.g. == 401)
    resp = client.get(f"/sessions/{invalid_session_id}/close")
    assert resp.status_code == 200