from uuid import uuid4

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


def test_password_hashing():
    password = "TestPassword123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_access_token():
    user_id = str(uuid4())

    token = create_access_token(user_id)

    payload = decode_access_token(token)

    assert payload["sub"] == user_id
    assert "exp" in payload
    assert "iat" in payload