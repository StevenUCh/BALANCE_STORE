# ==========================
# Dockerfile para Flask + pdfkit + wkhtmltopdf
# ==========================

# Imagen base
FROM python:3.9-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libxext6 \
    curl \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Instalar wkhtmltopdf (estático)
RUN curl -L -o wkhtmltox.tar.xz https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox-0.12.6-1_linux-generic-amd64.tar.xz \
    && tar -xJf wkhtmltox.tar.xz \
    && mv wkhtmltox/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf \
    && rm -rf wkhtmltox.tar.xz wkhtmltox

# Crear directorio de la app
WORKDIR /app

# Copiar archivos Python y templates
COPY requirements.txt .
COPY . .

# Instalar dependencias Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponer puerto (Railway asignará uno dinámico, pero usamos 5716 para local)
EXPOSE 5716

# Comando para ejecutar la app
CMD ["python", "app.py"]
