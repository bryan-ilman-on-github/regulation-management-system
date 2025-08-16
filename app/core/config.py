import os
from dotenv import load_dotenv

# This is for local development without Docker
load_dotenv()

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL")

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")