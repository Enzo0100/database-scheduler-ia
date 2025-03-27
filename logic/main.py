import json
import os
import re
from dotenv import load_dotenv
from utils.converts import process_video_to_markdown
from data.jsons import amazon_json, datasets_RAG_json
from data.datasets import (
    insere_novo_dataset,
    insere_files,
)
from data.aws import (
    acessar_bucket_s3,
    baixar_documentos_faltantes_s3
)


load_dotenv()
PASTA_DOWNLOADS = os.getenv("OUTPUT_FILES", "downloads")
api_key = os.getenv("API_RAG_KEY")
address = os.getenv("URL")

# Criar a pasta de downloads se não existir
if not os.path.exists(PASTA_DOWNLOADS):
    os.makedirs(PASTA_DOWNLOADS)

# baixar_faltantes = input("Deseja baixar arquivos da S3? (y/N)")

def sincronizar_datasets(address):
    """
    Sincroniza os datasets locais com os armazenados na API RAGFlow.
    - Verifica os arquivos existentes no AWS S3 e na API.
    - Cria novos datasets se necessário.
    - Baixa arquivos ausentes do S3 e os envia para a API.
    """

    Api_tenant = {
        "1": "ragflow-JjZDcwOTdhMGE2MzExZjBiNTAzMDI0Mm",
    }
    print("\n🔄 Iniciando sincronização de datasets...\n")

    # 1. Atualiza a lista de arquivos no S3
    acessar_bucket_s3()
    # 2. Carregar os JSONs de referência
    videos_por_id = amazon_json()  # { tenant_id: { categoria: [arquivos] } }
    datasets, ids = datasets_RAG_json()  # { categoria: [arquivos] }
    ids_mapping = {entry[1]: entry[0] for entry in ids}

    # 3. Comparação entre os arquivos do S3 e os datasets do RAGFlow
    documentos_faltando = {}  # {tenant_id: {categoria: [arquivos]}}
    novos_datasets = {}  # {tenant_id: [categorias]}

    for tenant_id, categorias in videos_por_id.items():
        for categoria, arquivos_s3 in categorias.items():
            if categoria in datasets:
                print(categoria)
                categoria_path = os.path.join("downloads", categoria)
                arquivos_api = datasets[categoria]  # Arquivos já cadastrados na API
                dataset_id = ids_mapping.get(categoria)
                mapeamento_extensoes = {}
                for nome in arquivos_s3:
                    partes = nome.rsplit('.', 1)  # Divide no último ponto
                    if len(partes) > 1:
                        mapeamento_extensoes[partes[0]] = partes[1]  # Ex: {"video": "mp4"}
                    else:
                        mapeamento_extensoes[nome] = ''  # Caso não tenha extensão

                # 2. Lista de arquivos no S3 sem extensão
                arquivos_sem_extensao = [nome.rsplit('.', 1)[0] for nome in arquivos_s3]

                # 3. Identificar arquivos que estão no S3, mas não na API
                arquivos_faltantes = list(set(arquivos_sem_extensao) - set(arquivos_api))
                print(set(arquivos_api))
                print(f"ARQUIVOS FALTANDO: {arquivos_faltantes}")

                # 4. Adicionar as extensões originais aos arquivos faltantes
                arquivos_faltantes_com_extensao = [
                    f"{faltante}.{mapeamento_extensoes[faltante]}" if mapeamento_extensoes[faltante] else faltante
                    for faltante in arquivos_faltantes
                ]

                # Resultado final

                if arquivos_faltantes:
                    if tenant_id not in documentos_faltando:
                        documentos_faltando[tenant_id] = {}
                    documentos_faltando[tenant_id][categoria] = arquivos_faltantes
                    # if baixar_faltantes == "y":
                    #Adicionar função de adicionar no banco de dados
                    baixar_documentos_faltantes_s3(arquivos_faltantes_com_extensao, tenant_id, categoria)
                    for file_name in arquivos_faltantes_com_extensao:
                        name = file_name
                        name = name.replace(".mp3", "").replace(".mp4", "")
                        print(f"FILE NAMEEEEE = {file_name}")
                        md_file_path = process_video_to_markdown(
                            video_path=f"downloads/{categoria}/{file_name}",
                            output_dir=f"downloads/{categoria}",
                            file= name
                        )

                    # Passo 3: Remover todos os .mp3 e .mp4 da pasta após o processamento
                                        # Criar a pasta de downloads se não existir
                    if not os.path.exists(categoria_path):
                        os.makedirs(categoria_path)
                    for item in os.listdir(categoria_path):
                        if item.lower().endswith(".mp4") or item.lower().endswith(".mp3"):
                            os.remove(os.path.join(categoria_path, item))
                            print(f"Removido: {item}")
                            
                if not os.path.exists(categoria_path):
                    os.makedirs(categoria_path)
                # Passo 4: Listar os arquivos que sobraram (por ex., .md)
                arquivos_restantes = os.listdir(categoria_path)
                print(f"Arquivos restantes na pasta {categoria}: {arquivos_restantes}")
                try:
                    print("FOI")
                    insere_files(dataset_id=dataset_id,categoria=categoria,arquivos=arquivos_restantes,api_key=Api_tenant[f'{tenant_id}'],address=address)
                    categoria_path = os.path.join("downloads", categoria)
                    for item in os.listdir(categoria_path):
                        if item.lower().endswith(".md"):
                            os.remove(os.path.join(categoria_path, item))
                            print(f"Removido: {item}")
                except KeyError as e:
                    print(f"Não tem o {tenant_id} como Usuário, favor criar\n\n {e}")

            else:
                # Se a categoria não existe no RAGFlow, criar dataset e adicionar todos os arquivos do S3
                print(f"📌 Criando dataset para categoria '{categoria}' no tenant '{tenant_id}'...")
                
                if tenant_id not in novos_datasets:
                    novos_datasets[tenant_id] = []
                novos_datasets[tenant_id].append(categoria)

                dataset_id = insere_novo_dataset(categoria)

                if dataset_id:
                    categoria_path = os.path.join("downloads", categoria)

                    # Obter TODOS os arquivos da categoria no S3
                    arquivos_categoria_s3 = [nome for nome in arquivos_s3]
                    print(f"Arquivos do S3 para categoria '{categoria}': {arquivos_categoria_s3}")

                    if tenant_id not in documentos_faltando:
                        documentos_faltando[tenant_id] = {}
                    documentos_faltando[tenant_id][categoria] = arquivos_categoria_s3  

                    # if baixar_faltantes == "y":
                    baixar_documentos_faltantes_s3(arquivos_categoria_s3, tenant_id, categoria)

                    for file_name in arquivos_categoria_s3:
                        name = file_name.replace(".mp3", "").replace(".mp4", "")
                        md_file_path = process_video_to_markdown(
                            video_path=f"downloads/{categoria}/{file_name}",
                            output_dir=f"downloads/{categoria}",
                            file=name
                        )
                    if not os.path.exists(categoria_path):
                        os.makedirs(categoria_path)

                    for item in os.listdir(categoria_path):
                        if item.lower().endswith(".mp4") or item.lower().endswith(".mp3"):
                            os.remove(os.path.join(categoria_path, item))
                            print(f"Removido: {item}")

                    arquivos_restantes = os.listdir(categoria_path)
                    print(f"Arquivos restantes na pasta {categoria}: {arquivos_restantes}")

                    try:
                        insere_files(dataset_id=dataset_id, categoria=categoria, arquivos=arquivos_restantes, 
                                    api_key=Api_tenant[f'{tenant_id}'], address=address)
                        
                        for item in os.listdir(categoria_path):
                            if item.lower().endswith(".md"):
                                os.remove(os.path.join(categoria_path, item))
                                print(f"Removido: {item}")

                    except KeyError as e:
                        print(f"Erro ao inserir arquivos: {e}")

    # 6. Exibir o resumo final
    print("\n📌 Resumo da Sincronização:\n")

    if novos_datasets:
        print("\n🚀 **Novos Datasets Criados:**")
        print(json.dumps(novos_datasets, indent=4, ensure_ascii=False))

    print("\n✅ Sincronização finalizada!\n")


# 🔹 **Executar manualmente para testar**
if __name__ == "__main__":
    sincronizar_datasets(address)
