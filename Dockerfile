FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    curl \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libxext6 \
    libjpeg62-turbo \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Instalar wkhtmltopdf precompilado para Debian Bullseye
RUN curl -L -o wkhtmltox.deb https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bullseye_amd64.deb \
    && apt-get update && apt-get install -y ./wkhtmltox.deb \
    && rm wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5716
CMD ["python", "app.py"]
