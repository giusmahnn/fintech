from dotenv import load_dotenv
from .base import *
import os
load_dotenv()

DEBUG = True
BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8000')
