import os
import requests
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Função para enviar transcrição e prompt para o modelo GPT-4o mini ou outros modelos
def send_to_gpt4o_mini(markdown_file, user_request, model):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Determinar o endpoint correto com base no modelo
    if model in ["gpt-4", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"]:  # Modelos de chat
        openai_url = "https://api.openai.com/v1/chat/completions"
        is_chat_model = True


    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }

    with open(markdown_file, 'r') as f:
        md_content = f.read()

    if is_chat_model:
        # Para modelos de chat, o formato de dados precisa ser diferente
        data = {
            "model": model,
            "messages": [{"role": "system", "content": "Você é um assistente de IA."},
                         {"role": "user", "content": f"{md_content}\n\n{user_request}"}],
            "max_tokens": 3000,
            "temperature": 0.7
        }

    response = requests.post(openai_url, headers=headers, json=data)

    if response.status_code == 200:
        if is_chat_model:
            return response.json().get("choices")[0].get("message").get("content")
        else:
            return response.json().get("choices")[0].get("text")
    else:
        raise Exception(f"Erro ao enviar para GPT-4o mini: {response.status_code}, {response.text}")
