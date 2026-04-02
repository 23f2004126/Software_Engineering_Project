from passlib.context import CryptContext

# Initialize Passlib context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Maximum password length for bcrypt in bytes
MAX_BCRYPT_LENGTH = 72


def _truncate_password(password: str) -> bytes:
    """
    Encode the password to UTF-8 and truncate to MAX_BCRYPT_LENGTH bytes.
    Ensures multibyte characters do not exceed bcrypt's limit.
    """
    if not password:
        raise ValueError("Password cannot be empty")

    encoded = password.encode("utf-8")
    if len(encoded) > MAX_BCRYPT_LENGTH:
        encoded = encoded[:MAX_BCRYPT_LENGTH]
    return encoded


def hash_password(password: str) -> str:
    password_bytes = _truncate_password(password)
    return pwd_context.hash(password_bytes)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = _truncate_password(plain_password)
    except ValueError:
        return False
    return pwd_context.verify(password_bytes, hashed_password)
