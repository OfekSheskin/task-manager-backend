"""Password hashing + JWT helpers.

Hashing is wired up for you with the `bcrypt` library. You'll implement the JWT
functions in Phase 2 (auth).

Note: bcrypt only hashes the first 72 bytes of a password — validate/limit password
length in your Phase 2 registration schema.
"""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage in users.password_hash."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# TODO (Phase 2): implement using python-jose (jose.jwt):
#   def create_access_token(subject: str) -> str: ...
#   def decode_access_token(token: str) -> dict: ...
