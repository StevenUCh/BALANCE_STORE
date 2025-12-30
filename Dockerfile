# Usamos una imagen ligera de Python 3.9
FROM python:3.9-alpine

# Evitar bytecode y usar stdout sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias necesarias para wkhtmltopdf y fonts
RUN apk add --no-cache \
    bash \
    curl \
    ttf-dejavu \
    fontconfig \
    libxext \
    libxrender \
    libjpeg-turbo \
    xorg-server \
    xvfb

# Descargar wkhtmltopdf versión Linux genérica (amd64)
RUN curl -L -o wkhtmltox.tar.xz https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox-0.12.6-1_linux-generic-amd64.tar.xz \
    && apk add --no-cache xz \
    && tar -xJf wkhtmltox.tar.xz \
    && mv wkhtmltox/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf \
    && rm -rf wkhtmltox.tar.xz wkhtmltox \
    && apk del xz

# Crear directorio de la app
WORKDIR /app

# Copiar archivos de la app
COPY requirements.txt .
COPY . .

# Instalar dependencias Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponer puerto que usará Flask
EXPOSE 5716

# Comando para ejecutar la app con xvfb para que wkhtmltopdf funcione sin pantalla
CMD ["xvfb-run", "--auto-servernum", "--server-args='-screen 0 1024x768x24'", "python", "app.py"]
