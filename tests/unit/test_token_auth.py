from src.auth.token_auth import parse_bearer_token, resolve_user_id


def test_parse_bearer_token():
    assert parse_bearer_token(None) is None
    assert parse_bearer_token("") is None
    assert parse_bearer_token("Bearer abc") == "abc"
    assert parse_bearer_token("bearer abc") == "abc"
    assert parse_bearer_token("Bearer   abc  ") == "abc"
    assert parse_bearer_token("Token abc") is None


def test_resolve_user_id():
    tokens = {"t1": "u1"}
    assert resolve_user_id(None, tokens) is None
    assert resolve_user_id("bad", tokens) is None
    assert resolve_user_id("t1", tokens) == "u1"
