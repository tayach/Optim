import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    DEBUG = os.environ.get("FLASK_ENV") == "development"
    API_URL = os.environ.get("API_URL")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_DEFAULT_MODEL = os.environ.get("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")
    OPENAI_STRUCTURED_MODEL = os.environ.get(
        "OPENAI_STRUCTURED_MODEL", OPENAI_DEFAULT_MODEL
    )
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    FIREBASE_CREDENTIALS = os.environ.get("FIREBASE_CREDENTIALS")
    REDIS_URL = os.environ.get("REDIS_URL")
