"""
HTTP Honeypot - Captura ataques web
Detecta SQL injection, XSS, path traversal y otros ataques HTTP
Guarda todos los ataques en PostgreSQL
"""

import socket
import threading
import time
import os
import sys
from datetime import datetime
from urllib.parse import unquote

# Agregar parent directory al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import logger, log_attack, log_connection, log_error
import config
import database


class HTTPHoneypot:
    """
    Servidor HTTP honeypot que captura ataques web
    """
    
    def __init__(self, host=config.HONEYPOT_HOST, port=config.HONEYPOT_HTTP_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.request_count = 0
    
    def start(self):
        """Iniciar servidor HTTP"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            self.running = True
            
            logger.info(f"HTTP Honeypot iniciado en {self.host}:{self.port}")
            
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
        except Exception as e:
            log_error(e, "al iniciar HTTP Honeypot")
            raise
    
    def _accept_connections(self):
        """Aceptar conexiones HTTP"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.request_count += 1
                
                client_thread = threading.Thread(
                    target=self._handle_request,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except KeyboardInterrupt:
                logger.info("\nHTTP Honeypot detenido por usuario")
                self.stop()
                break
            except Exception as e:
                if self.running:
                    log_error(e, "al aceptar conexion HTTP")
    
    def _handle_request(self, client_socket, client_address):
        """Manejar request HTTP individual"""
        try:
            request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
            
            if not request_data:
                return
            
            # Parsear request
            lines = request_data.split('\n')
            if not lines:
                return
            
            request_line = lines[0].strip()
            headers = {}
            
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            # Extraer datos del request
            parts = request_line.split()
            if len(parts) < 2:
                return
            
            method = parts[0]
            path = unquote(parts[1])
            user_agent = headers.get('User-Agent', 'Unknown')
            
            client_ip = client_address[0]
            
            logger.info(f"HTTP Request | IP: {client_ip} | {method} {path}")
            
            # Detectar tipo de ataque
            attack_type = self._detect_attack_type(path, request_data)
            severity = self._get_severity(attack_type)
            
            # Guardar en BD
            attack_id = database.insert_attack(
                source_ip=client_ip,
                service="HTTP",
                attack_type=attack_type,
                payload=f"{method} {path}",
                user_agent=user_agent,
                headers=str(headers),
                severity=severity
            )
            
            if attack_id:
                logger.info(f"Ataque HTTP guardado | ID: {attack_id} | Tipo: {attack_type}")
            
            # Loguear para analisis
            attack_data = {
                'source_ip': client_ip,
                'service': 'HTTP',
                'attack_type': attack_type,
                'payload': f"{method} {path}",
                'user_agent': user_agent,
                'severity': severity
            }
            log_attack(attack_data)
            
            # Responder con 200 OK (enganar al atacante)
            response = self._build_response()
            client_socket.sendall(response.encode())
            
        except Exception as e:
            log_error(e, f"al manejar request HTTP de {client_address[0]}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _detect_attack_type(self, path, request_data):
        """Detectar tipo de ataque basado en el path y datos"""
        path_lower = path.lower()
        request_lower = request_data.lower()
        
        # SQL Injection
        for pattern in config.SQL_INJECTION_PATTERNS:
            if pattern in path_lower or pattern in request_lower:
                return "SQL_INJECTION"
        
        # XSS
        for pattern in config.XSS_PATTERNS:
            if pattern in path_lower or pattern in request_lower:
                return "XSS"
        
        # Path Traversal
        for pattern in config.PATH_TRAVERSAL_PATTERNS:
            if pattern in path:
                return "PATH_TRAVERSAL"
        
        # Bots / Scanners
        if any(bot in path_lower for bot in ['admin', 'phpmyadmin', 'wp-admin', '.env', '.git']):
            return "SCANNER"
        
        # Request normal (sospechoso por estar en honeypot)
        return "SUSPICIOUS_REQUEST"
    
    def _get_severity(self, attack_type):
        """Determinar severidad del ataque"""
        high_severity = ['SQL_INJECTION', 'XSS']
        medium_severity = ['PATH_TRAVERSAL', 'SCANNER']
        
        if attack_type in high_severity:
            return "HIGH"
        elif attack_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _build_response(self):
        """Construir respuesta HTTP falsa"""
        html = config.HTTP_RESPONSE_BODY
        
        response = f"""HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: {len(html)}
Server: Apache/2.4.41 (Ubuntu)
Connection: close

{html}"""
        
        return response
    
    def stop(self):
        """Detener servidor HTTP"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("HTTP Honeypot detenido")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Funcion principal"""
    logger.info("=" * 70)
    logger.info("HONEYPOT-LAB - HTTP HONEYPOT v0.1")
    logger.info("=" * 70)
    logger.info(f"Inicializando HTTP Honeypot...")
    logger.info(f"Host: {config.HONEYPOT_HOST}")
    logger.info(f"Puerto: {config.HONEYPOT_HTTP_PORT}")
    logger.info("=" * 70)
    
    # Inicializar BD
    logger.info("\nVerificando base de datos...")
    try:
        database.init_database()
        logger.info("Base de datos lista\n")
    except Exception as e:
        logger.error(f"Error con BD: {e}")
        return
    
    # Crear y iniciar servidor
    honeypot = HTTPHoneypot(
        host=config.HONEYPOT_HOST,
        port=config.HONEYPOT_HTTP_PORT
    )
    
    try:
        honeypot.start()
        
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\nDeteniendo HTTP Honeypot...")
        honeypot.stop()
    except Exception as e:
        log_error(e, "en main")
        honeypot.stop()


if __name__ == "__main__":
    main()
