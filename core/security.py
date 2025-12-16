import bcrypt

def hash_password(password: str) -> str:
    """Хеширование пароля"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Проверка пароля"""
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)