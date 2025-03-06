import os
import subprocess

def split_audio(input_file):
    output_files = []

    # Verificar o tamanho do arquivo em MB
    file_size_mb = os.path.getsize(input_file) / (1024 * 1024)

    # Se o arquivo for menor que 10 MB, não precisa dividir
    if file_size_mb <= 10:
        output_files.append(input_file)
        return output_files

    # Caso contrário, dividir o áudio em partes de 10 MB
    duration = float(subprocess.getoutput(f'ffprobe -i {input_file} -show_entries format=duration -v quiet -of csv="p=0"'))
    bitrate = float(subprocess.getoutput(f'ffprobe -i {input_file} -show_entries format=bit_rate -v quiet -of csv="p=0"'))

    target_size_mb = 10
    target_size_bits = target_size_mb * 8 * 1024 * 1024  # 10 MB em bits
    part_duration = target_size_bits / bitrate  # Duração de cada parte em segundos

    for i in range(0, int(duration), int(part_duration)):
        output_file = f"audio_part_{i}.mp3"
        subprocess.run(['ffmpeg', '-i', input_file, '-ss', str(i), '-t', str(part_duration), '-c', 'copy', output_file])
        output_files.append(output_file)

    return output_files


def convert_mp4_to_mp3(input_file):
    # Verifica se o arquivo de entrada é um arquivo MP4
    if not input_file.endswith('.mp4'):
        raise ValueError("O arquivo de entrada não é um arquivo MP4.")

    # Define o nome do arquivo de saída com extensão .mp3
    output_file = input_file.replace('.mp4', '.mp3')
    
    # Executa o comando ffmpeg para converter MP4 para MP3 com taxa de bits de 320k
    try:
        subprocess.run(['ffmpeg', '-i', input_file, '-b:a', '320k', '-map', 'a', output_file], check=True)
        print(f"Conversão concluída. Arquivo MP3 salvo como {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a conversão: {e}")
        raise

    return output_file
