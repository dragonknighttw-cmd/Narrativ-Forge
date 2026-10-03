from app.services.passwords import hash_password, verify_password


def test_password_hash_verifies_only_the_original_password():
    password = "change-me-123456"
    encoded = hash_password(password)

    assert encoded.startswith("$pbkdf2_sha256$")
    assert verify_password(password, encoded)
    assert not verify_password("wrong-password", encoded)
