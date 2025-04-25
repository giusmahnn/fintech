from dotenv import load_dotenv
from .base import *
import os
load_dotenv()

DEBUG = True
BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8000')


EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

ANYMAIL = {
    "BREVO_API_KEY": os.getenv("EMAIL_API_KEY"),
}