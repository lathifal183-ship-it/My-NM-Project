import hashlib, hmac, secrets
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
from app.database import get_db

def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210000)
    return salt.hex() + "$" + digest.hex()

def verify_password(password, stored):
    try:
        salt, expected = stored.split("$", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 210000)
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False

def create_user(username, email, password):
    with get_db() as db:
        try:
            cur = db.execute("INSERT INTO users(username,email,password_hash) VALUES(?,?,?)",
                             (username.strip(), email.strip().lower(), hash_password(password)))
            return {"id": cur.lastrowid, "username": username.strip(), "email": email.strip().lower()}
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise ValueError("That username or email is already registered.") from exc
            raise

def authenticate(username, password):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE", (username.strip(),)).fetchone()
    if not row or not verify_password(password, row["password_hash"]):
        return None
    return {"id": row["id"], "username": row["username"], "email": row["email"]}

def create_access_token(user):
    exp = datetime.now(timezone.utc) + timedelta(minutes=60)
    return jwt.encode({"sub": str(user["id"]), "username": user["username"], "exp": exp},
                      settings.secret_key, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])

def get_user_by_id(user_id):
    with get_db() as db:
        row = db.execute("SELECT id,username,email FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None
