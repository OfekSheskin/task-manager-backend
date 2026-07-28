import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage in users.password_hash."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())
