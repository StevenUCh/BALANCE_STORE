# --- Dockerfile para Flask + wkhtmltopdf en Railway ---

# Base image
FROM python:3.9-slim-buster

# Variables de entorno para no pedir confirmación en apt y no generar archivos de cache
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libxext6 \
    libjpeg62-turbo \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar wkhtmltopdf precompilado para Debian Buster
RUN curl -L -o wkhtmltox.deb https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt-get update && apt-get install -y ./wkhtmltox.deb \
    && rm wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app
WORKDIR /app

# Copiar requirements.txt e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la app
COPY . .

# Exponer el puerto que usa Flask
EXPOSE 5716

# Comando por defecto para correr Flask
CMD ["python", "app.py"]
