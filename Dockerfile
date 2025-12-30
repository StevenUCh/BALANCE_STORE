# --------------------------------------
# Dockerfile para Flask + pdfkit + wkhtmltopdf
# Compatible con Railway
# --------------------------------------

# Imagen base de Python 3.9 slim (Debian Buster)
FROM python:3.9-slim

# --------------------------------------
# Instalar dependencias del sistema necesarias
# --------------------------------------
RUN apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------
# Descargar e instalar wkhtmltopdf (Debian Buster, amd64)
# --------------------------------------
RUN curl -L -o wkhtmltox.tar.xz https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox-0.12.6-1_linux-generic-amd64.tar.xz \
    && tar -xJf wkhtmltox.tar.xz \
    && mv wkhtmltox/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf \
    && rm -rf wkhtmltox.tar.xz wkhtmltox

# --------------------------------------
# Crear directorio de trabajo
# --------------------------------------
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# --------------------------------------
# Instalar dependencias Python
# --------------------------------------
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# --------------------------------------
# Variables de entorno
# --------------------------------------
ENV PORT 5716
EXPOSE 5716

# --------------------------------------
# Comando para correr la app con Gunicorn
# --------------------------------------
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5716"]
