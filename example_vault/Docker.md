---
cards-deck: DevOps
status: completo
tipo_nota: herramienta
created: 2025-01-15
---

# Docker

Docker es una plataforma de **contenedorización** que permite empaquetar aplicaciones con todas sus dependencias en contenedores portables.

## Conceptos Clave

### Contenedor
Un contenedor es una instancia ejecutable de una imagen. Contiene:
- La aplicación
- Dependencias
- Configuración
- Todo lo necesario para ejecutarse

### Imagen
Una imagen es una plantilla read-only para crear contenedores. Se construye a partir de un Dockerfile.

### Dockerfile
Archivo de texto con instrucciones para construir una imagen:

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## Ventajas

- **Portabilidad**: "Funciona en mi máquina" → "Funciona en todas las máquinas"
- **Aislamiento**: Cada contenedor está aislado
- **Eficiencia**: Más ligero que máquinas virtuales
- **Reproducibilidad**: Mismo ambiente en dev, test y producción

## Comandos Básicos

```bash
# Construir imagen
docker build -t mi-app .

# Ejecutar contenedor
docker run -p 8000:8000 mi-app

# Listar contenedores
docker ps

# Ver logs
docker logs <container-id>

# Detener contenedor
docker stop <container-id>
```

## Docker Compose

Para aplicaciones multi-contenedor:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: secret
```

## Casos de Uso

- Desarrollo local consistente
- CI/CD pipelines
- Microservicios
- Despliegue de aplicaciones

## Relaciones

- Similar a máquinas virtuales pero más eficiente
- Complementa [[Kubernetes]] para orquestación
- Usado en muchos workflows de [[DevOps]]
