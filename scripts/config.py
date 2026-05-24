"""Configuración centralizada para honeypot-lab"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)

# ============ CONFIGURACIÓN DE RED ============
HONEYPOT_HOST = os.getenv('HONEYPOT_HOST', '0.0.0.0')
HONEYPOT_SSH_PORT = int(os.getenv('HONEYPOT_SSH_PORT', 22))
HONEYPOT_HTTP_PORT = int(os.getenv('HONEYPOT_HTTP_PORT', 80))
HONEYPOT_HTTPS_PORT = int(os.getenv('HONEYPOT_HTTPS_PORT', 443))
HONEYPOT_DNS_PORT = int(os.getenv('HONEYPOT_DNS_PORT', 53))

# ============ CONFIGURACIÓN DE BASE DE DATOS ============
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://honeypot_user:honeypot_pass@localhost:5432/honeypot_db'
)

if DATABASE_URL:
    from urllib.parse import urlparse
    db_url = urlparse(DATABASE_URL)
    DB_HOST = db_url.hostname or 'localhost'
    DB_PORT = db_url.port or 5432
    DB_NAME = db_url.path.lstrip('/')
    DB_USER = db_url.username
    DB_PASSWORD = db_url.password
else:
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'honeypot_db'
    DB_USER = 'honeypot_user'
    DB_PASSWORD = 'honeypot_pass'

# ============ CONFIGURACIÓN DE LOGGING ============
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / 'honeypot.log'
LOG_FORMAT = (
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# ============ CONFIGURACIÓN DE GEOLOCALIZACIÓN ============
GEOIP_DB_PATH = os.getenv(
    'GEOIP_DB_PATH',
    os.path.expanduser('~/geoip-data/GeoLite2-City.mmdb')
)
ENABLE_GEOIP = os.getenv('ENABLE_GEOIP', 'True').lower() == 'true'

# ============ CONFIGURACIÓN DE APLICACIÓN ============
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 5000))

# ============ CONFIGURACIÓN DE HONEYPOT ============
SSH_BANNER = "SSH-2.0-OpenSSH_7.4"
SSH_KEY_SIZE = 2048
SSH_MAX_AUTH_ATTEMPTS = 3
SSH_TIMEOUT = 60

HTTP_RESPONSE_CODE = 200
HTTP_RESPONSE_BODY = "<html><body><h1>Welcome</h1></body></html>"

# ============ PATRONES DE DETECCIÓN ============
SQL_INJECTION_PATTERNS = ["union", "select", "insert", "update", "delete", "drop", "exec", "script", "alert"]
XSS_PATTERNS = ["<script", "javascript:", "onerror=", "onload=", "alert("]
PATH_TRAVERSAL_PATTERNS = ["../", "..\\", "%2e%2e", "...."]

# ============ CONFIGURACIÓN DE RETENCIÓN ============
RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', 90))

CONFIG_SUMMARY = {
    "SSH": f"{HONEYPOT_HOST}:{HONEYPOT_SSH_PORT}",
    "HTTP": f"{HONEYPOT_HOST}:{HONEYPOT_HTTP_PORT}",
    "Database": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
    "Logs": str(LOG_DIR),
}
