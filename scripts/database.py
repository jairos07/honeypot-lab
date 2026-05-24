"""
Módulo de base de datos para honeypot-lab
Maneja conexiones a PostgreSQL y operaciones CRUD de ataques
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from contextlib import contextmanager
import config
from logger import logger, log_db_event, log_error

# ============================================================================
# CLASE DE CONEXIÓN A BD
# ============================================================================

class DatabaseConnection:
    """Maneja la conexión a PostgreSQL"""
    
    def __init__(self):
        self.host = config.DB_HOST
        self.port = config.DB_PORT
        self.database = config.DB_NAME
        self.user = config.DB_USER
        self.password = config.DB_PASSWORD
        self.connection = None
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=5
            )
            logger.info(f"✅ Conexión a BD exitosa: {self.host}:{self.port}/{self.database}")
            return self.connection
        except Exception as e:
            logger.error(f"❌ No se pudo conectar a BD: {e}")
            raise
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.connection:
            self.connection.close()
            logger.info("✅ Desconectado de BD")
    
    @contextmanager
    def get_cursor(self, dict_cursor=False):
        """Context manager para cursores"""
        if not self.connection:
            self.connect()
        
        cursor_type = RealDictCursor if dict_cursor else None
        cursor = self.connection.cursor(cursor_factory=cursor_type)
        
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            log_error(e, "en operación de BD")
            raise
        finally:
            cursor.close()


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================
db = DatabaseConnection()


# ============================================================================
# FUNCIONES CRUD - ATAQUES
# ============================================================================

def insert_attack(
    source_ip: str,
    service: str,
    attack_type: str,
    payload: str,
    user_agent: str = None,
    headers: str = None,
    country: str = None,
    city: str = None,
    latitude: float = None,
    longitude: float = None,
    severity: str = "MEDIUM",
    username: str = None,
    password: str = None
) -> int:
    """
    Insertar un ataque en la BD
    
    Args:
        source_ip: IP del atacante
        service: SSH, HTTP, DNS, etc.
        attack_type: BRUTE_FORCE, SQL_INJECTION, XSS, etc.
        payload: Datos del ataque capturados
        user_agent: User-Agent del request (para HTTP)
        headers: Headers capturados (JSON string)
        country: País detectado por GeoIP
        city: Ciudad detectada por GeoIP
        latitude: Latitud
        longitude: Longitud
        severity: LOW, MEDIUM, HIGH, CRITICAL
        username: Usuario intentado (SSH)
        password: Contraseña intentada (SSH)
    
    Returns:
        ID del ataque insertado
    """
    query = """
    INSERT INTO attacks (
        timestamp, source_ip, service, attack_type, payload,
        user_agent, headers, country, city, latitude, longitude, 
        severity, username, password
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    RETURNING id;
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, (
                datetime.now(),
                source_ip,
                service,
                attack_type,
                payload,
                user_agent,
                headers,
                country,
                city,
                latitude,
                longitude,
                severity,
                username,
                password
            ))
            attack_id = cursor.fetchone()[0]
            logger.info(f"📍 Ataque insertado | ID: {attack_id} | IP: {source_ip} | Tipo: {attack_type}")
            return attack_id
    except Exception as e:
        log_error(e, "al insertar ataque")
        return None


def get_recent_attacks(limit: int = 100) -> list:
    """
    Obtener ataques recientes
    
    Args:
        limit: Número máximo de ataques a retornar
    
    Returns:
        Lista de ataques (dicts)
    """
    query = """
    SELECT * FROM attacks
    ORDER BY timestamp DESC
    LIMIT %s;
    """
    
    try:
        with db.get_cursor(dict_cursor=True) as cursor:
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            logger.debug(f"Obtenidos {len(results)} ataques recientes")
            return results if results else []
    except Exception as e:
        log_error(e, "al obtener ataques recientes")
        return []


def get_attack_by_id(attack_id: int) -> dict:
    """
    Obtener un ataque por ID
    
    Args:
        attack_id: ID del ataque
    
    Returns:
        Datos del ataque (dict)
    """
    query = "SELECT * FROM attacks WHERE id = %s;"
    
    try:
        with db.get_cursor(dict_cursor=True) as cursor:
            cursor.execute(query, (attack_id,))
            result = cursor.fetchone()
            return result if result else None
    except Exception as e:
        log_error(e, "al obtener ataque por ID")
        return None


def get_attacks_by_ip(source_ip: str, limit: int = 50) -> list:
    """
    Obtener ataques de una IP específica
    
    Args:
        source_ip: IP del atacante
        limit: Número máximo de ataques
    
    Returns:
        Lista de ataques de esa IP
    """
    query = """
    SELECT * FROM attacks
    WHERE source_ip = %s
    ORDER BY timestamp DESC
    LIMIT %s;
    """
    
    try:
        with db.get_cursor(dict_cursor=True) as cursor:
            cursor.execute(query, (source_ip, limit))
            results = cursor.fetchall()
            logger.debug(f"Obtenidos {len(results
