from app.core.auth import create_access_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    hashed = hash_password("a-long-password-123")
    assert hashed != "a-long-password-123"
    assert verify_password("a-long-password-123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_contains_subject() -> None:
    import jwt

    from app.core.config import get_settings

    token = create_access_token("candidate-1")
    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=[get_settings().jwt_algorithm])
    assert payload["sub"] == "candidate-1"
