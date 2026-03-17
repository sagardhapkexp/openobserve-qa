import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants moved from api_helper.py
BASE_URL = os.getenv("BASE_URL", "http://localhost:5080")
ORG = os.getenv("ORG", "default")
EMAIL = os.getenv("EMAIL", "root@example.com")
PASSWORD = os.getenv("PASSWORD", "Complexpass#123")
