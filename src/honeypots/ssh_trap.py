"""
SSH Honeypot - Captura y analiza intentos de login SSH
Emula un servidor SSH falso para detectar ataques de fuerza bruta
Guarda todos los ataques en PostgreSQL
"""

import socket
import threading
import time
import paramiko
import os
import sys
from datetime import datetime

# Agregar parent directory al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import logger, log_attack, log_connection, log_error
import config
import database

# ============================================================================
# CONFIGURACIÓN SSH
# ============================================================================

# Generar key RSA para el servidor (simulado)
RSA_KEY = paramiko.RSAKey.generate(config.SSH_KEY_SIZE)


class SSHHoneypot(paramiko.ServerInterface):
    """
    Interfaz de servidor SSH que finge ser un servidor real
    pero captura todos los intentos de login
    """
    
    def __init__(self, client_address):
        self.client_ip = client_address[0]
        self.client_port = client_address[1]
        self.auth_attempts = 0
        self.username = None
        self.password = None
        
        # Loguear conexión
        log_connection(self.client_ip, "SSH", config.HONEYPOT_SSH_PORT)
        logger.info(f"🔌 Conexión SSH recibida desde {self.client_ip}:{self.client_port}")
    
    def check_auth_password(self, username, password):
        """
        Se llama cuando el cliente intenta autenticarse con usuario/contraseña
        SIEMPRE rechazamos, pero capturamos el intento
        """
        self.auth_attempts += 1
        self.username = username
        self.password = password
        
        logger.warning(
            f"🔓 SSH LOGIN ATTEMPT | "
            f"IP: {self.client_ip} | "
            f"Username: {username} | "
            f"Password: {password} | "
            f"Attempt: {self.auth_attempts}"
        )
        
        # Determinar severidad basado en número de intentos
        if self.auth_attempts == 1:
            severity = "LOW"
            attack_type = "LOGIN_ATTEMPT"
        elif self.auth_attempts <= 3:
            severity = "MEDIUM"
            attack_type = "BRUTE_FORCE"
        else:
            severity = "HIGH"
            attack_type = "BRUTE_FORCE"
        
        # Crear payload
        payload = f"username={username};password={password};attempt={self.auth_attempts}"
        
        # GUARDAR EN BASE DE DATOS
        attack_id = database.insert_attack(
            source_ip=self.client_ip,
            service="SSH",
            attack_type=attack_type,
            payload=payload,
            severity=severity,
            username=username,
            password=password
        )
        
        if attack_id:
            logger.info(f"✅ Ataque guardado en BD | ID: {attack_id}")
        else:
            logger.error(f"❌ Error al guardar ataque en BD")
        
        attack_data = {
            'source_ip': self.client_ip,
            'service': 'SSH',
            'attack_type': attack_type,
            'payload': payload,
            'username': username,
            'password': password,
            'severity': severity,
        }
        log_attack(attack_data)
        
        if self.auth_attempts >= config.SSH_MAX_AUTH_ATTEMPTS:
            logger.critical(
                f"🚨 BRUTE FORCE CRÍTICO DETECTADO | "
                f"IP: {self.client_ip} | Intentos: {self.auth_attempts}"
            )
        
        time.sleep(1)
        return paramiko.AUTH_FAILED
    
    def check_auth_publickey(self, username, key):
        """
        Se llama cuando el cliente intenta autenticarse con clave pública
        """
        self.auth_attempts += 1
        self.username = username
        
        key_type = key.get_name()
        
        logger.warning(
            f"🔐 SSH PUBKEY ATTEMPT | "
            f"IP: {self.client_ip} | "
            f"Username: {username} | "
            f"Key Type: {key_type}"
        )
        
        payload = f"username={username};key_type={key_type};key_bits={key.get_bits()}"
        
        attack_id = database.insert_attack(
            source_ip=self.client_ip,
            service="SSH",
            attack_type="PUBKEY_AUTH_ATTEMPT",
            payload=payload,
            severity="MEDIUM",
            username=username
        )
        
        if attack_id:
            logger.info(f"✅ Intento de pubkey guardado | ID: {attack_id}")
        
        time.sleep(1)
        return paramiko.AUTH_FAILED
    
    def check_channel_request(self, kind, chanid):
        """
        Se llama cuando el cliente solicita un canal
        """
        logger.debug(f"SSH CHANNEL REQUEST | IP: {self.client_ip} | Kind: {kind}")
        
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def get_allowed_auths(self, username):
        """
        Indica qué métodos de autenticación soportamos
        """
        return 'password,publickey'
    
    def check_channel_subsystem_request(self, channel, name):
        """
        Se llama cuando el cliente solicita un subsistema (ej: sftp)
        """
        logger.warning(
            f"⚠️  SSH SUBSYSTEM REQUEST | IP: {self.client_ip} | "
            f"Subsystem: {name}"
        )
        
        payload = f"subsystem={name}"
        
        database.insert_attack(
            source_ip=self.client_ip,
            service="SSH",
            attack_type="SUBSYSTEM_REQUEST",
            payload=payload,
            severity="LOW"
        )
        
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED


class SSHHoneypotServer:
    """
    Servidor SSH Honeypot que escucha conexiones entrantes
    """
    
    def __init__(self, host=config.HONEYPOT_HOST, port=config.HONEYPOT_SSH_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.client_count = 0
    
    def start(self):
        """Iniciar el servidor SSH"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            self.running = True
            
            logger.info(
                f"🚀 SSH Honeypot iniciado en {self.host}:{self.port} "
                f"(Banner: {config.SSH_BANNER})"
            )
            
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
        except PermissionError:
            logger.error(
                f"❌ Permiso denegado para puerto {self.port}. "
                f"Necesitas sudo o cambia el puerto en .env"
            )
            raise
        except Exception as e:
            log_error(e, "al iniciar SSH Honeypot")
            raise
    
    def _accept_connections(self):
        """Aceptar conexiones entrantes"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.client_count += 1
                
                logger.info(f"👤 Cliente #{self.client_count} conectado: {client_address[0]}")
                
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except KeyboardInterrupt:
                logger.info("\n⏹️  SSH Honeypot detenido por el usuario")
                self.stop()
                break
            except Exception as e:
                if self.running:
                    log_error(e, "al aceptar conexión SSH")
    
    def _handle_client(self, client_socket, client_address):
        """Manejar cliente SSH individual"""
        try:
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(RSA_KEY)
            
            server = SSHHoneypot(client_address)
            transport.start_server(server=server)
            
            channel = transport.accept(20)
            
            if channel is None:
                logger.debug(f"No channel abierto desde {client_address[0]}")
            else:
                channel.close()
            
            transport.close()
            
        except paramiko.AuthenticationException:
            logger.debug(f"Autenticación falló desde {client_address[0]}")
        except paramiko.SSHException as e:
            logger.debug(f"SSH Exception desde {client_address[0]}: {e}")
        except Exception as e:
            log_error(e, f"al manejar cliente SSH {client_address[0]}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def stop(self):
        """Detener el servidor SSH"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("✅ SSH Honeypot detenido")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal"""
    logger.info("=" * 70)
    logger.info("HONEYPOT-LAB - SSH HONEYPOT v0.1 (CON BD)")
    logger.info("=" * 70)
    logger.info(f"Inicializando SSH Honeypot...")
    logger.info(f"Host: {config.HONEYPOT_HOST}")
    logger.info(f"Puerto: {config.HONEYPOT_SSH_PORT}")
    logger.info(f"Banner: {config.SSH_BANNER}")
    logger.info(f"Max intentos auth: {config.SSH_MAX_AUTH_ATTEMPTS}")
    logger.info("=" * 70)
    
    # Inicializar base de datos
    logger.info("\n📁 Inicializando base de datos...")
    try:
        database.init_database()
        logger.info("✅ Base de datos lista\n")
    except Exception as e:
        logger.error(f"❌ Error al inicializar BD: {e}")
        logger.error("Asegúrate de que PostgreSQL está corriendo y configurado correctamente")
        return
    
    # Crear y iniciar servidor
    honeypot = SSHHoneypotServer(
        host=config.HONEYPOT_HOST,
        port=config.HONEYPOT_SSH_PORT
    )
    
    try:
        honeypot.start()
        
        # Mantener el servidor corriendo
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\nDeteniendo SSH Honeypot...")
        honeypot.stop()
    except Exception as e:
        log_error(e, "en main")
        honeypot.stop()


if __name__ == "__main__":
    # Verificar permisos
    if os.geteuid() != 0 and config.HONEYPOT_SSH_PORT < 1024:
        logger.warning(
            f"⚠️  Advertencia: Necesitas sudo para usar puertos < 1024 "
            f"(intentando puerto {config.HONEYPOT_SSH_PORT})"
        )
        logger.info("Opción 1: Ejecuta con 'sudo python3 honeypot/ssh_trap.py'")
        logger.info("Opción 2: Cambia HONEYPOT_SSH_PORT en .env a uno > 1024 (ej: 2222)")
    
    main()
