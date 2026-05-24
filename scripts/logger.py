"""Sistema de logging centralizado usando loguru"""
import sys
from loguru import logger
from pathlib import Path
import config

# Remover handler default
logger.remove()

# Crear directorio de logs
Path(config.LOG_DIR).mkdir(exist_ok=True, parents=True)

# Logs a consola
logger.add(
    sys.stdout,
    format=config.LOG_FORMAT,
    level=config.LOG_LEVEL,
    colorize=True,
)

# Logs a archivo
logger.add(
    str(config.LOG_FILE),
    format=config.LOG_FORMAT,
    level=config.LOG_LEVEL,
    rotation="500 MB",
    retention="90 days",
    compression="zip",
)

# Loggers por categoría
attack_logger = logger.bind(name="ATTACKS")
db_logger = logger.bind(name="DATABASE")
connection_logger = logger.bind(name="CONNECTIONS")
error_logger = logger.bind(name="ERRORS")

def log_attack(attack_data: dict):
    """Loguea un ataque detectado"""
    attack_logger.warning(
        f"ATAQUE DETECTADO | IP: {attack_data.get('source_ip')} | "
        f"Servicio: {attack_data.get('service')} | Tipo: {attack_data.get('attack_type')}"
    )

def log_connection(source_ip: str, service: str, port: int):
    """Loguea una conexión entrante"""
    connection_logger.info(f"Conexión | IP: {source_ip} | Servicio: {service} | Puerto: {port}")

def log_db_event(event: str, details: str = ""):
    """Loguea eventos de base de datos"""
    db_logger.info(f"{event} | {details}")

def log_error(error: Exception, context: str = ""):
    """Loguea errores"""
    error_logger.error(f"ERROR {context} | {type(error).__name__}: {str(error)}")

__all__ = ['logger', 'attack_logger', 'db_logger', 'log_attack', 'log_connection', 'log_db_event', 'log_error']
