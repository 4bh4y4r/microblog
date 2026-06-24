import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir,'app.db')
    TURNSTILE_SITE_KEY = "0x4AAAAAADqezx0SZ3yVl3dU"
    TURNSTILE_SECRET_KEY = "0x4AAAAAADqezzOLc0FT9zpJdHJoAEoF3DA"

    