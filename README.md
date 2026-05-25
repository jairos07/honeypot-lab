# Honeypot Lab - Security Research Project

Un framework modular de honeypot desarrollado para capturar y analizar ataques en tiempo real, implementado como proyecto de aprendizaje en ciberseguridad.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)

---

##  Descripción del Proyecto

Este proyecto nace de la necesidad de entender cómo funcionan los ataques informáticos en entornos reales. **Honeypot Lab** es un framework que simula servicios vulnerables (SSH, HTTP) para capturar intentos de intrusión, analizar patrones de ataque y almacenar datos forenses para su posterior análisis.

###  Objetivos del Proyecto

1. **Capturar ataques reales** - Implementar honeypots funcionales que registren intentos de acceso
2. **Análisis de patrones** - Almacenar y clasificar ataques por tipo, origen y severidad
3. **Aprendizaje práctico** - Comprender arquitecturas de seguridad y técnicas de detección
4. **Investigación** - Generar datos reales para estudiar comportamiento de atacantes

---

##  Características Implementadas

### Honeypots Activos
- **SSH Honeypot** - Simula servidor SSH en puerto 2222
  - Captura intentos de login y brute force
  - Registra credenciales intentadas
  - Clasifica por nivel de severidad
  
- **HTTP Honeypot** - Simula servidor web en puerto 8080
  - Detecta SQL Injection
  - Identifica ataques XSS
  - Captura Path Traversal
  - Reconoce scanners y bots

### Base de Datos
- PostgreSQL para almacenamiento persistente
- Tabla `attacks` con índices optimizados
- Almacena: IP origen, timestamp, tipo de ataque, payload, severidad
- Funciones de análisis y estadísticas

### Herramientas de Testing
- Simulador de ataques automatizado
- Genera tráfico SSH y HTTP malicioso
- Múltiples modos: rápido, stress test, ataques mixtos
- Útil para validar detección sin exponer el honeypot

---

##  ¿Por qué es útil este proyecto?

### Para Estudiantes de Ciberseguridad
- **Práctica real**: Ves cómo funcionan los ataques sin arriesgar sistemas productivos
- **Datos forenses**: Analizas payloads reales de ataques capturados
- **Arquitectura modular**: Estudias diseño de sistemas de seguridad

### Para Investigación
- **Patrones de ataque**: Identifica tendencias (IPs más activas, tipos de ataque frecuentes)
- **Threat Intelligence**: Genera indicadores de compromiso (IoCs)
- **Análisis de malware**: Captura binarios y scripts maliciosos

### Para Portafolio Profesional
- Demuestra conocimiento en Python, bases de datos, redes y seguridad
- Proyecto completo con arquitectura limpia y documentación
- Aplicación práctica de conceptos de ciberseguridad

---

## ¿Qué aprendí desarrollando este proyecto?

### Conocimientos Técnicos
- **Programación de sockets**: Implementación de servidores TCP personalizados
- **Protocolos de red**: SSH (con Paramiko), HTTP a bajo nivel
- **Bases de datos**: PostgreSQL, diseño de esquemas, queries optimizadas
- **Logging avanzado**: Sistema centralizado con Loguru
- **Arquitectura modular**: Separación de responsabilidades, configuración centralizada

### Seguridad y Análisis
- **Detección de ataques**: Patrones de SQL injection, XSS, path traversal
- **Clasificación de amenazas**: Niveles de severidad, tipos de atacantes
- **Análisis forense**: Captura y almacenamiento de evidencias
- **Threat modeling**: Diseño de honeypots efectivos

### DevOps y Buenas Prácticas
- **Control de versiones**: Git, commits semánticos, branches
- **Virtualización**: Proxmox, VMs aisladas, networking
- **Gestión de dependencias**: Virtual environments, requirements.txt
- **Documentación**: README, guías técnicas

---

##  Nota sobre el uso de IA

**El código Python de este proyecto fue desarrollado con asistencia de Claude AI .**

La IA fue utilizada como herramienta de apoyo para:
- Acelerar el desarrollo de módulos funcionales
- Implementar mejores prácticas de programación
- Debugging y optimización de código
- Generación de documentación técnica

**Mi rol en el proyecto:**
- Diseño de arquitectura y requisitos
- Configuración de infraestructura (Proxmox, PostgreSQL, networking)
- Testing y validación de funcionalidades
- Toma de decisiones técnicas
- Documentación y presentación

---

## Demostración

El proyecto captura ataques SSH y HTTP en tiempo real, almacenándolos en PostgreSQL para análisis posterior.

### Ejemplos de ataques capturados:
- Brute force SSH con diccionarios de contraseñas comunes
- SQL injection en parámetros de URL
- XSS reflejado en formularios web
- Path traversal intentando acceder a `/etc/passwd`
- Scanners buscando `/admin`, `/phpmyadmin`, `.env`

Ver capturas en `docs/screenshots/`

---

##  Stack Tecnológico

| Categoría | Tecnologías |
|-----------|-------------|
| **Lenguaje** | Python 3.12 |
| **Framework Web** | Flask (futuro dashboard) |
| **Base de Datos** | PostgreSQL 14 |
| **Logging** | Loguru |
| **Networking** | Sockets, Paramiko (SSH) |
| **Virtualización** | Proxmox VE |
| **Control de versiones** | Git + GitHub |

---

##  Estructura del Proyecto

honeypot-lab/
├── src/
│   ├── core/              # Módulos principales (config, logger, database)
│   ├── honeypots/         # Honeypots SSH y HTTP
│   └── utils/             # Herramientas (simulador de ataques)
├── docs/                  # Documentación técnica
├── tests/                 # Tests y validaciones
└── README.md              # Este archivo

Ver documentacion tecnica para detalles de implementación.

---

##  Quick Start

### Requisitos
- Ubuntu Server 22.04+
- Python 3.10+
- PostgreSQL 12+
- 2GB RAM, 2 vCPU

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/honeypot-lab.git
cd honeypot-lab

# Crear virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env

# Inicializar base de datos
python3 -c "from src.core.database import init_database; init_database()"

# Ejecutar honeypots
python3 src/honeypots/ssh_trap.py    # Terminal 1
python3 src/honeypots/http_trap.py   # Terminal 2
```

Ver [SETUP.md](docs/SETUP.md) para guía detallada.

---

##  Advertencias de Seguridad

- **NO exponer a Internet**: Usar solo en redes aisladas/LAB
- **Entorno controlado**: Proxmox, VMs aisladas, sin acceso a producción
- **Solo para investigación**: No usar en infraestructura real
- **Revisar logs**: Puede capturar información sensible no intencional

---

##  Próximas Mejoras

- [ ] Dashboard web con visualizaciones (Flask + Chart.js)
- [ ] API REST para consultar ataques
- [ ] Integración con GeoIP para mapear orígenes
- [ ] Detección con Machine Learning
- [ ] Exportación de reportes PDF
- [ ] Docker + Docker Compose para despliegue rápido
- [ ] CI/CD con GitHub Actions

---

##  Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

---

## Autor: Jairo mosteiro

Proyecto desarrollado como parte de mi formación en ciberseguridad.

### Contacto:
- GitHub: [@jairos07](https://github.com/jairos07)
- Linkedin: https://www.linkedin.com/in/jairo-mosteiro-4a2aa138b/

---

##  Agradecimientos

- **Claude AI** por asistencia en desarrollo de código
- **Comunidad de seguridad open-source** por inspiración
- **Proyectos Kippo y Cowrie** como referencia de honeypots

---

**Desarrollado con fines educativos | Usar responsablemente**