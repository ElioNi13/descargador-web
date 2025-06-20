import os
import re
from urllib.parse import quote
from flask import Flask, request, jsonify, send_from_directory
from yt_dlp import YoutubeDL

# Le decimos a Flask que los archivos estáticos (como index.html) están en la misma carpeta.
app = Flask(__name__, static_folder='.', static_url_path='')

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Opciones BASE para yt-dlp.
YDL_OPTS_BASE = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
    'noplaylist': True,
    'keepvideo': False,
    'socket_timeout': 120, # Aumentamos la paciencia
    'rm_cachedir': True,
    # --- Disfraz Final: Usar cookies del navegador ---
    # Esto intenta simular una sesión de navegador real. Es el método más potente.
    # Puede que no funcione en Render si no encuentra un perfil de navegador.
    'cookies_from_browser': ('chrome',),
}

@app.route('/')
def index():
    print("--- Petición recibida. Sirviendo index.html... ---")
    return app.send_static_file('index.html')

@app.route('/api/process', methods=['POST'])
def process_video():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality', '192') # Calidad por defecto si no se especifica

    if not url:
        return jsonify({'error': 'URL no proporcionada'}), 400

    try:
        ydl_opts = YDL_OPTS_BASE.copy()
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality, # Usamos la calidad seleccionada
        }]

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_id = info_dict.get('id')
            video_title = info_dict.get('title', 'Título Desconocido')
            video_uploader = info_dict.get('uploader', 'Artista Desconocido')
            video_thumbnail = info_dict.get('thumbnail')
            video_duration = info_dict.get('duration_string', 'N/A')

            if not video_id:
                return jsonify({'error': 'No se pudo obtener la ID del video.'}), 500

            mp3_filename = f"{video_id}.mp3"

            # --- LÓGICA PARA EL NUEVO NOMBRE DE ARCHIVO ---
            safe_title = re.sub(r'[\\/*?:"<>|]', "", video_title)
            friendly_filename = f"EasyMP3Downloader - {safe_title}.mp3"
            encoded_filename = quote(friendly_filename)
            download_url_with_name = f"/downloads/{mp3_filename}?filename={encoded_filename}"
            
            return jsonify({
                'download_url': download_url_with_name,
                'title': video_title,
                'uploader': video_uploader,
                'thumbnail': video_thumbnail,
                'duration': video_duration,
            })
            
    except Exception as e:
        return jsonify({'error': f"Un error ocurrió: {str(e)}"}), 500

@app.route('/downloads/<path:filename>')
def serve_download(filename):
    download_name = request.args.get('filename', filename)
    return send_from_directory(
        DOWNLOAD_FOLDER, 
        filename, 
        as_attachment=True,
        download_name=download_name
    )

if __name__ == '__main__':
    print("--- Servidor listo. Por favor, abre http://127.0.0.1:8000 en tu navegador. ---")
    app.run(host='0.0.0.0', port=8000)
