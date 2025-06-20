# Usar una imagen base de Python oficial
FROM python:3.9-slim

# Instalar ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación
COPY . .

# Exponer el puerto que usará Gunicorn
EXPOSE 8000

# Comando para arrancar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]