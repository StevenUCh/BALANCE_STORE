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
RUN curl -L -o wkhtmltox.deb https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt-get install -y ./wkhtmltox.deb \
    && rm wkhtmltox.deb

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
