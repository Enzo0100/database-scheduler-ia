import os
import uuid
import subprocess
from utils.modules.audio_processing import split_audio
from utils.modules.whisper_api import send_to_whisper
from utils.modules.markdown_utils import save_transcription_markdown

def process_video_to_markdown(video_path,output_dir,file):
    """
    Recebe o caminho de um arquivo de vídeo (ex.: .mp4) e gera um arquivo Markdown 
    com a transcrição do áudio (via Whisper). Retorna o caminho do arquivo .md gerado.

    Parâmetros:
    -----------
    video_path : str
        Caminho para o arquivo de vídeo (ex.: '/caminho/para/video.mp4').
    output_dir : str, opcional
        Caminho para a pasta de saída onde será salvo o .md. 
        Se não fornecido, a função gera uma nova pasta dentro de "outputs".

    Retorna:
    --------
    str
        Caminho para o arquivo Markdown (.md) com a transcrição.
    """

    def convert_mp4_to_mp3(input_file, out_dir):
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        mp3_path = os.path.join(out_dir, f"{base_name}.mp3")
        print(out_dir)

        # Ajusta o caminho relativo
        input_file = os.path.abspath(input_file)  

        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_file}")

        try:
            result = subprocess.run([
                'ffmpeg',
                '-i', input_file,
                '-b:a', '320k',
                '-map', 'a',
                mp3_path
            ], check=True, capture_output=True, text=True)
            
            print(f"Conversão concluída: {mp3_path}")
            return mp3_path

        except subprocess.CalledProcessError as e:
            print(f"Erro ao converter {input_file} para MP3.")
            print(f"Saída do erro:\n{e.stderr}")
            raise


    # Garante que exista uma pasta de saída
    if output_dir is None:
        output_id = str(uuid.uuid4())
        output_dir = os.path.join("outputs", output_id)
    os.makedirs(output_dir, exist_ok=True)

    # Verifica extensão para conversão
    ext = os.path.splitext(video_path)[1].lower()
    if ext == '.mp4':
        audio_path = convert_mp4_to_mp3(video_path, output_dir)
    else:
        # Se for .mp3 ou .wav, apenas copia/usa o próprio arquivo
        # (Você pode adaptar para realmente copiar, se desejar)
        audio_path = video_path

    # 1) Divide o áudio em partes menores
    audio_parts = split_audio(audio_path)

    # 2) Transcreve cada parte com Whisper
    transcriptions = []
    for part in audio_parts:
        text = send_to_whisper(part)
        transcriptions.append(text)

    # 3) Salva a transcrição final como Markdown
    md_file_path = os.path.join(output_dir, f"{file}.md")
    save_transcription_markdown(transcriptions, md_file_path)

    # Retorna o caminho do .md gerado
    return md_file_path
