"""
Simulador de ataques para honeypot-lab
Genera ataques SSH y HTTP para testing
"""

import socket
import time
import random
import requests
from datetime import datetime

# Configuracion
SSH_HOST = "localhost"
SSH_PORT = 2222
HTTP_HOST = "localhost"
HTTP_PORT = 8080

# Datos de prueba
SSH_USERS = [
    "admin", "root", "test", "user", "administrator",
    "postgres", "mysql", "oracle", "ubuntu", "pi"
]

SSH_PASSWORDS = [
    "admin", "password", "123456", "password123", "admin123",
    "root", "12345678", "qwerty", "test", "letmein"
]

HTTP_PAYLOADS = {
    "SQL_INJECTION": [
        "/index.php?id=1' OR '1'='1",
        "/login.php?user=admin'--",
        "/search?q='; DROP TABLE users--",
        "/api/users?id=1 UNION SELECT * FROM passwords",
        "/product.php?id=1' AND 1=1--"
    ],
    "XSS": [
        "/search?q=<script>alert(1)</script>",
        "/comment?text=<img src=x onerror=alert(1)>",
        "/page?name=<script>document.cookie</script>",
        "/input?data=<iframe src=evil.com>",
        "/search?q=<svg onload=alert(1)>"
    ],
    "PATH_TRAVERSAL": [
        "/download?file=../../../../etc/passwd",
        "/read?path=../../etc/shadow",
        "/view?page=../../../config.php",
        "/file?name=....//....//etc/hosts",
        "/get?file=..%2f..%2f..%2fetc%2fpasswd"
    ],
    "SCANNER": [
        "/admin",
        "/phpmyadmin",
        "/wp-admin",
        "/.env",
        "/.git/config",
        "/backup.sql",
        "/config.php",
        "/database.yml"
    ]
}


def simulate_ssh_attack(num_attempts=5):
    """Simular ataque de fuerza bruta SSH"""
    print(f"\n[SSH] Iniciando simulacion de {num_attempts} intentos de login...")
    
    for i in range(num_attempts):
        username = random.choice(SSH_USERS)
        password = random.choice(SSH_PASSWORDS)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((SSH_HOST, SSH_PORT))
            
            # Enviar banner SSH falso
            banner = sock.recv(1024)
            
            print(f"  [{i+1}/{num_attempts}] Intentando {username}:{password}")
            
            sock.close()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error en intento {i+1}: {e}")
    
    print(f"[SSH] Simulacion completada: {num_attempts} intentos")


def simulate_http_attack(num_requests=10):
    """Simular ataques HTTP"""
    print(f"\n[HTTP] Iniciando simulacion de {num_requests} requests...")
    
    attack_count = {
        "SQL_INJECTION": 0,
        "XSS": 0,
        "PATH_TRAVERSAL": 0,
        "SCANNER": 0
    }
    
    for i in range(num_requests):
        # Seleccionar tipo de ataque aleatorio
        attack_type = random.choice(list(HTTP_PAYLOADS.keys()))
        payload = random.choice(HTTP_PAYLOADS[attack_type])
        
        url = f"http://{HTTP_HOST}:{HTTP_PORT}{payload}"
        
        try:
            response = requests.get(url, timeout=3)
            attack_count[attack_type] += 1
            print(f"  [{i+1}/{num_requests}] {attack_type}: {payload[:50]}...")
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  Error en request {i+1}: {e}")
    
    print(f"\n[HTTP] Simulacion completada:")
    for attack_type, count in attack_count.items():
        print(f"  - {attack_type}: {count} requests")


def simulate_mixed_attacks(duration_seconds=30):
    """Simular ataques mixtos durante un tiempo determinado"""
    print(f"\n[MIXED] Iniciando simulacion mixta por {duration_seconds} segundos...")
    
    start_time = time.time()
    request_count = 0
    
    while time.time() - start_time < duration_seconds:
        # Alternar entre SSH y HTTP
        if random.random() < 0.5:
            # Ataque SSH
            simulate_ssh_attack(num_attempts=1)
        else:
            # Ataque HTTP
            simulate_http_attack(num_requests=1)
        
        request_count += 1
        time.sleep(random.uniform(0.5, 2))
    
    print(f"\n[MIXED] Simulacion completada: {request_count} ataques en {duration_seconds}s")


def main():
    """Menu principal"""
    print("=" * 70)
    print("HONEYPOT-LAB - SIMULADOR DE ATAQUES")
    print("=" * 70)
    print("\nOpciones:")
    print("1. Simular ataque SSH (fuerza bruta)")
    print("2. Simular ataques HTTP (SQL, XSS, etc)")
    print("3. Simular ataques mixtos (SSH + HTTP)")
    print("4. Ataque rapido (5 SSH + 10 HTTP)")
    print("5. Estres test (100 requests)")
    print("0. Salir")
    
    choice = input("\nSelecciona opcion: ").strip()
    
    if choice == "1":
        num = int(input("Numero de intentos SSH [10]: ") or "10")
        simulate_ssh_attack(num_attempts=num)
    
    elif choice == "2":
        num = int(input("Numero de requests HTTP [20]: ") or "20")
        simulate_http_attack(num_requests=num)
    
    elif choice == "3":
        duration = int(input("Duracion en segundos [30]: ") or "30")
        simulate_mixed_attacks(duration_seconds=duration)
    
    elif choice == "4":
        print("\n[QUICK] Ejecutando ataque rapido...")
        simulate_ssh_attack(num_attempts=5)
        simulate_http_attack(num_requests=10)
        print("\n[QUICK] Ataque rapido completado")
    
    elif choice == "5":
        print("\n[STRESS] Ejecutando stress test...")
        simulate_http_attack(num_requests=100)
        print("\n[STRESS] Stress test completado")
    
    elif choice == "0":
        print("\nSaliendo...")
    
    else:
        print("\nOpcion invalida")


if __name__ == "__main__":
    main()

