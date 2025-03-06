import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

    # Pegar configurações do ambiente
BUCKET_NAME = os.getenv("BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
PASTA_DOWNLOADS = os.getenv("OUTPUT_FILES", "downloads")  # Usa 'downloads' como padrão

def acessar_bucket_s3(BUCKET_NAME=os.getenv("BUCKET_NAME"),AWS_ACCESS_KEY=os.getenv("AWS_ACCESS_KEY"),AWS_SECRET_KEY=os.getenv("AWS_SECRET_KEY"),AWS_REGION=os.getenv("AWS_REGION")):
    """Acessa um bucket S3 específico e lista seus objetos."""
    
    # Criar cliente S3 com as credenciais carregadas
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    # Listar objetos dentro do bucket
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        
        if 'Contents' in response:
            print(f"Objetos encontrados no bucket '{BUCKET_NAME}'")
            # for obj in response['Contents']:
            #     print(f"- {obj['Key']}")
        else:
            print(f"O bucket '{BUCKET_NAME}' está vazio ou não tem permissões para listar objetos.")
    
    except Exception as e:
        print(f"Erro ao acessar o bucket '{BUCKET_NAME}':", e)

def listar_videos_por_pastas(BUCKET_NAME=os.getenv("BUCKET_NAME"),AWS_ACCESS_KEY=os.getenv("AWS_ACCESS_KEY"),AWS_SECRET_KEY=os.getenv("AWS_SECRET_KEY"),AWS_REGION=os.getenv("AWS_REGION")):
    """Lista os vídeos de um bucket, separando-os por ID e pastas."""

    # Criar cliente S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    # Dicionário para armazenar vídeos por ID e suas pastas
    estrutura = {}

    try:
        # Listar objetos dentro do bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']  # Nome completo do arquivo no S3
                
                # Verifica se é um vídeo (ajuste conforme os formatos desejados)
                if key.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv')):
                    partes = key.split('/')  # Divide pelo separador de pastas "/"

                    if len(partes) > 2:  # Para garantir que tem ID/Pasta/Arquivo
                        id_pasta = partes[1]  # Primeiro nível é o ID
                        pasta = partes[2]  # Segundo nível é a pasta
                        video = partes[-1]  # Nome do vídeo

                        # Criar estrutura do ID se não existir
                        if id_pasta not in estrutura:
                            estrutura[id_pasta] = {}

                        # Criar a pasta dentro do ID se não existir
                        if pasta not in estrutura[id_pasta]:
                            estrutura[id_pasta][pasta] = []

                        # Adicionar o vídeo na pasta correta
                        estrutura[id_pasta][pasta].append(video)
                    else:
                        # Caso o vídeo esteja na raiz do bucket
                        if "Raiz" not in estrutura:
                            estrutura["Raiz"] = {}
                        if "Sem Pasta" not in estrutura["Raiz"]:
                            estrutura["Raiz"]["Sem Pasta"] = []
                        estrutura["Raiz"]["Sem Pasta"].append(video)

        else:
            print("O bucket está vazio ou sem permissões para listar objetos.")

    except Exception as e:
        print(f"Erro ao acessar o bucket '{BUCKET_NAME}':", e)
        return None

    estrutura_formatada = {}  # Criar um dicionário para armazenar a estrutura corrigida

    for id_pasta, pastas in estrutura.items():
        if id_pasta not in estrutura_formatada:
            estrutura_formatada[id_pasta] = {}  # Criar chave para cada ID

        for pasta, videos in pastas.items():
            if pasta not in estrutura_formatada[id_pasta]:
                estrutura_formatada[id_pasta][pasta] = []  # Criar chave para cada pasta dentro do ID
            
            estrutura_formatada[id_pasta][pasta].extend(videos)  # Adicionar vídeos à pasta correspondente

    return estrutura_formatada

def baixar_documentos_faltantes_s3(arquivos_faltantes, tenant_id, categoria):
    """
    Baixa arquivos específicos de uma pasta do S3 para a pasta local.
    Retorna a lista de arquivos baixados ou existentes.
    """
    # Configurações do ambiente
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    PASTA_DOWNLOADS = os.getenv("OUTPUT_FILES", "downloads")  # Padrão 'downloads'

    # Garantir pasta de downloads
    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)

    # Criar cliente S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    arquivos_baixados = []

    for arquivo in arquivos_faltantes:
        # Montar caminhos
        caminho_s3 = f"videos/{tenant_id}/{categoria}/lesson/{arquivo}"
        nome_arquivo = os.path.basename(arquivo)
        caminho_local = os.path.join(f'{PASTA_DOWNLOADS}/{categoria}', nome_arquivo)
        print(caminho_local)
        # Criar o diretório se não existir
        os.makedirs(os.path.dirname(caminho_local), exist_ok=True)
        # Verificar se já existe localmente
        if os.path.exists(caminho_local):
            print(f"⏩ Arquivo já existente: {nome_arquivo}")
            arquivos_baixados.append(caminho_local)
            continue

        # Tentar download
        try:
            s3_client.download_file(BUCKET_NAME, caminho_s3, caminho_local)
            arquivos_baixados.append(caminho_local)
            print(f"✅ Baixado: {nome_arquivo}")
        except s3_client.exceptions.NoSuchKey:
            print(f"❌ Arquivo não encontrado no S3: {caminho_s3}")
        except Exception as e:
            print(f"⚠️ Erro ao baixar {nome_arquivo}: {str(e)}")

    return arquivos_baixados

