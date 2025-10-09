# 🚛 Sistema de Gestión de Combustible - LogincoCobustible

[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![DigitalOcean](https://img.shields.io/badge/DigitalOcean-Spaces-blue.svg)](https://digitalocean.com/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Business%20API-green.svg)](https://business.whatsapp.com/)

Sistema integral de gestión de combustible para flotas de vehículos con integración completa de WhatsApp, reportes automáticos y sistema de mantenimiento preventivo.

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API y Integraciones](#-api-y-integraciones)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Comandos de Gestión](#-comandos-de-gestión)
- [Despliegue](#-despliegue)
- [Contribución](#-contribución)

## 🚀 Características Principales

### 📊 Gestión de Combustible
- **Registro de combustible** con fotos de tickets
- **Cálculo automático** de costos y estadísticas
- **Actualización automática** del kilometraje de vehículos
- **Reportes mensuales** automáticos con Excel

### 🚛 Gestión de Flota
- **Catálogo de equipos** (vehículos) con especificaciones
- **Gestión de operadores** y supervisores
- **Sistema de mantenimiento** preventivo automático
- **Alertas inteligentes** por tiempo y kilometraje

### 📱 Integración WhatsApp
- **Envío automático** de reportes mensuales
- **Mensajes interactivos** con botones
- **Alertas de operadores** inactivos
- **Webhook** para respuestas automáticas

### ☁️ Almacenamiento en la Nube
- **DigitalOcean Spaces** para archivos
- **Optimización automática** de imágenes
- **URLs públicas** para reportes
- **Backup automático** de archivos

### ⚙️ Automatización
- **Tareas programadas** con Celery
- **Notificaciones por email** con SendGrid
- **Reportes automáticos** mensuales
- **Verificación diaria** de mantenimientos

## 🏗️ Arquitectura del Sistema

```mermaid
graph TB
    A[Usuario Web] --> B[Django App]
    B --> C[Base de Datos PostgreSQL]
    B --> D[DigitalOcean Spaces]
    B --> E[Celery Workers]
    
    E --> F[WhatsApp Business API]
    E --> G[SendGrid Email]
    E --> H[Reportes Excel]
    
    I[Webhook WhatsApp] --> B
    J[Cron Jobs] --> E
    
    subgraph "Aplicaciones Django"
        K[equipo - Vehículos]
        L[operador - Conductores]
        M[registros - Combustible]
        N[mantenimientos - Mantenimiento]
    end
    
    B --> K
    B --> L
    B --> M
    B --> N
```

## 📦 Instalación

### Prerrequisitos
- Python 3.8+
- PostgreSQL
- Redis (para Celery)
- Cuenta de DigitalOcean Spaces
- WhatsApp Business API
- SendGrid API

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd LogincoCobustible
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Configurar base de datos
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Recopilar archivos estáticos
```bash
python manage.py collectstatic
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
DJANGO_DB_URL=postgresql://usuario:password@localhost:5432/combustible

# DigitalOcean Spaces
DO_SPACES_ACCESS_KEY=tu-access-key
DO_SPACES_SECRET_KEY=tu-secret-key
DO_SPACES_BUCKET_NAME=tu-bucket-name
DO_SPACES_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
DO_SPACES_REGION=nyc3
USE_SPACES=True

# WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID=tu-phone-number-id
WHATSAPP_ACCESS_TOKEN=tu-access-token
WHATSAPP_VERIFY_TOKEN=tu-verify-token

# SendGrid Email
EMAIL_HOST_PASSWORD=tu-sendgrid-api-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Configuración de Celery

```bash
# Iniciar worker de Celery
celery -A combustible worker --loglevel=info

# Iniciar beat scheduler
celery -A combustible beat --loglevel=info
```

## 🎯 Uso

### Acceso Web
```bash
python manage.py runserver
# Acceder a http://localhost:8000
```

### Funcionalidades Principales

#### 1. **Registro de Combustible**
- Ir a `/registros/`
- Agregar nuevo registro con foto del ticket
- El sistema actualiza automáticamente el kilometraje del vehículo

#### 2. **Gestión de Equipos**
- Ir a `/equipos/`
- Agregar nuevos vehículos
- Ver estado de mantenimiento

#### 3. **Sistema de Mantenimiento**
- Ir a `/mantenimientos/`
- Ver dashboard con alertas
- Programar y completar mantenimientos

#### 4. **Reportes Automáticos**
- Los reportes se envían automáticamente cada mes
- Incluyen estadísticas completas y archivo Excel

## 🔌 API y Integraciones

### WhatsApp Business API

#### Envío de Mensajes
```python
from whatsaap_service import WhatsAppBusinessService

service = WhatsAppBusinessService()
result = service.send_text_message("+525512345678", "Mensaje de prueba")
```

#### Webhook Configuration
```python
# URL del webhook: /webhook/whatsapp/
# Método: POST
# Verificación: GET con parámetros hub.mode, hub.verify_token, hub.challenge
```

### DigitalOcean Spaces

#### Subida de Archivos
```python
from combustible.storage_backends import MediaStorage

storage = MediaStorage()
file_url = storage.save('archivo.jpg', file_content)
```

### SendGrid Email

#### Envío de Emails
```python
from combustible.sendmail import sendMail

sendMail("destino@email.com", "Asunto", "Contenido HTML")
```

## 📁 Estructura del Proyecto

```
LogincoCobustible/
├── combustible/                 # Configuración principal de Django
│   ├── settings.py             # Configuraciones del proyecto
│   ├── urls.py                 # URLs principales
│   ├── storage_backends.py     # Configuración de almacenamiento
│   └── sendmail.py             # Servicio de email
├── equipo/                     # Aplicación de gestión de vehículos
│   ├── models.py               # Modelo Equipo
│   ├── views.py                # Vistas CRUD
│   └── templates/              # Plantillas HTML
├── operador/                   # Aplicación de gestión de operadores
│   ├── models.py               # Modelos Operador y Supervisor
│   └── views.py                # Vistas CRUD
├── registros/                  # Aplicación principal de combustible
│   ├── models.py               # Modelos Registro, ReporteGenerado, WhatsApp
│   ├── views.py                # Vistas y webhook de WhatsApp
│   ├── management/commands/    # Comandos personalizados
│   └── templates/              # Plantillas de reportes
├── mantenimientos/             # Sistema de mantenimiento
│   ├── models.py               # Modelos Mantenimiento, Notificacion
│   ├── views.py                # Dashboard y gestión
│   ├── tasks.py                # Tareas de Celery
│   └── templates/              # Plantillas de mantenimiento
├── static/                     # Archivos estáticos
├── templates/                  # Plantillas base
├── requirements.txt            # Dependencias Python
├── whatsaap_service.py         # Servicio de WhatsApp
└── manage.py                   # Script de gestión de Django
```

## 🛠️ Comandos de Gestión

### Reportes Mensuales
```bash
# Generar reporte del mes anterior
python manage.py enviar_reporte_mensual

# Generar reporte de mes específico
python manage.py enviar_reporte_mensual --mes 6 --año 2024

# Solo enviar por WhatsApp
python manage.py enviar_reporte_mensual --whatsapp-only

# Modo test (sin enviar)
python manage.py enviar_reporte_mensual --test
```

### Gestión de WhatsApp
```bash
# Listar contactos
python manage.py manage_whatsapp_contacts --list

# Agregar contacto
python manage.py manage_whatsapp_contacts --add "Juan Pérez,+525512345678,supervisor"

# Enviar mensaje de prueba
python manage.py manage_whatsapp_contacts --test "+525512345678"

# Sincronizar con operadores
python manage.py manage_whatsapp_contacts --sync
```

### Mantenimientos
```bash
# Verificar mantenimientos pendientes
python manage.py verificar_mantenimientos
```

## 🚀 Despliegue

### DigitalOcean App Platform

1. **Crear App en DigitalOcean**
2. **Configurar variables de entorno**
3. **Conectar repositorio Git**
4. **Configurar base de datos PostgreSQL**
5. **Configurar Redis para Celery**

### Configuración de Producción

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com']
USE_SPACES = True
```

### Tareas Programadas

```bash
# Configurar cron para Celery Beat
* * * * * cd /path/to/project && celery -A combustible beat --loglevel=info
```

## 📊 Monitoreo y Logs

### Logs del Sistema
- **Django**: Logs de aplicación en `logs/django.log`
- **Celery**: Logs de tareas asíncronas
- **WhatsApp**: Logs de webhooks y mensajes
- **Storage**: Logs de subida de archivos

### Métricas Importantes
- Registros de combustible por día/mes
- Operadores activos vs inactivos
- Mantenimientos pendientes/vencidos
- Uso de almacenamiento en Spaces

## 🔧 Mantenimiento

### Tareas Regulares
- **Diario**: Verificación automática de mantenimientos
- **Semanal**: Reportes de supervisores
- **Mensual**: Reportes completos de combustible
- **Trimestral**: Revisión de configuración de WhatsApp

### Backup
- **Base de datos**: Backup automático diario
- **Archivos**: Replicación en DigitalOcean Spaces
- **Configuración**: Backup de variables de entorno

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📞 Soporte

Para soporte técnico o consultas:
- **Email**: soporte@loginco.com.mx
- **WhatsApp**: +52 55 1234 5678
- **Issues**: Usar el sistema de issues de GitHub

## 📄 Licencia

Este proyecto es propiedad de Loginco y está destinado para uso interno de la empresa.

---

**Desarrollado con ❤️ por el equipo de Loginco**

*Sistema de Gestión de Combustible v2.0 - 2025*
