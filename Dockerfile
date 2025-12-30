FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libxext6 \
    curl \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar wkhtmltopdf versión precompilada
RUN curl -L -o wkhtmltox.deb https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt-get install -y ./wkhtmltox.deb \
    && rm wkhtmltox.deb

# Crear directorio de la app
WORKDIR /app

# Copiar archivos Python y templates
COPY requirements.txt .
COPY . .

# Instalar dependencias Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponer puerto
EXPOSE 5716

# Comando para ejecutar la app
CMD ["python", "app.py"]
