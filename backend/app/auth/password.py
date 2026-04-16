import hashlib
import hmac
import os

SALT_SEP = "$sha256$"


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a random salt."""
    salt = os.urandom(16).hex()
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{SALT_SEP}{salt}{SALT_SEP}{digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored hash."""
    try:
        parts = hashed_password.split(SALT_SEP)
        if len(parts) != 3:
            return False
        _, salt, stored_digest = parts
        digest = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return hmac.compare_digest(digest, stored_digest)
    except Exception:
        return False
