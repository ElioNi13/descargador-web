# Usar una imagen base de Python oficial y más reciente
FROM python:3.11-slim

# Instalar ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Actualizar yt-dlp a la última versión disponible para evitar bloqueos
RUN pip install --no-cache-dir -U yt-dlp

# Copiar el resto de los archivos de la aplicación
COPY . .

# Comando para arrancar la aplicación. Formato corregido para que Render entienda $PORT
CMD gunicorn --bind 0.0.0.0:$PORT app:app
