from data.aws import listar_videos_por_pastas
from data.datasets import datasets_RAG
import os
from dotenv import load_dotenv
import json

# Carregar as variáveis do arquivo .env
load_dotenv()
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")


def amazon_json():
    # Listar e exibir os vídeos organizados
    videos_por_id = listar_videos_por_pastas(BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION)
    print(json.dumps(videos_por_id, indent=4, ensure_ascii=False))
    return videos_por_id

def datasets_RAG_json():
    datasets, ids = datasets_RAG()
    for categoria in datasets:
        for i in range(len(datasets[categoria])):
            name = datasets[categoria][i].split('.')
            name.pop(-1)
            name = "".join(name)
            datasets[categoria][i] = name
    print(json.dumps(datasets, indent=4, ensure_ascii=False))
    return datasets, ids