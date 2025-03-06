import os
import requests
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Pega a chave da API do arquivo .env
openai_api_key = os.getenv("OPENAI_API_KEY")

def send_to_whisper(audio_file):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        'Authorization': f'Bearer {openai_api_key}',  # Usando a chave da API do .env
    }
    
    with open(audio_file, 'rb') as f:
        files = {
            'file': (audio_file, f),
            'model': (None, 'whisper-1'),
        }
        response = requests.post(url, headers=headers, files=files)
        
    if response.status_code == 200:
        return response.json().get("text")
    else:
        raise Exception(f"Erro ao transcrever {audio_file}: {response.status_code}, {response.text}")
