import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("API_RAG_KEY")
address = os.getenv("URL")
port_ds = os.getenv("DATASET_PORT")

def datasets_RAG(pages=1, page_size=300, orderby="name", desc="false",
                 api_key=api_key, address=address):
    """
    Obtém a lista de datasets e seus documentos organizados por nome do dataset.
    """
    print(api_key, address, port_ds)
    arquivos_por_nome = {}  # { nome_do_dataset: [documentos] }
    print("...........")
    for page in range(pages):
        # Criar a URL dinâmica para buscar os datasets
        url = f"http://{address}:{port_ds}/api/v1/datasets?page={page}&page_size={page_size}&orderby={orderby}&desc={desc}"

        # Definir os headers da requisição
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Processar os datasets recebidos
            dados = response.json()
            datasets = [[d["id"], d["name"]] for d in dados.get("data", [])]  # Pegando ID e Nome
            print(datasets)
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição dos datasets: {e}")
            return {}

        # Processar os documentos dentro de cada dataset
        for dataset_id, dataset_name in datasets:
            doc_url = f"http://{address}:{port_ds}/api/v1/datasets/{dataset_id}/documents?page={page}&page_size={page_size}&orderby={orderby}&desc={desc}"

            try:
                doc_response = requests.get(doc_url, headers=headers)
                doc_response.raise_for_status()

                doc_dados = doc_response.json()
                documentos = [doc["name"] for doc in doc_dados.get("data", {}).get("docs", [])]

            except requests.exceptions.RequestException as e:
                print(f"❌ Erro na requisição dos documentos do dataset {dataset_name}: {e}")
                continue

            # Adiciona os documentos ao dataset correspondente pelo Nome
            if dataset_name not in arquivos_por_nome:
                arquivos_por_nome[dataset_name] = []

            arquivos_por_nome[dataset_name].extend(documentos)

    # Exibir o dicionário formatado para depuração
    print("\n📌 Estrutura Final de Arquivos por Nome do Dataset:")
    print(json.dumps(arquivos_por_nome, indent=4, ensure_ascii=False))

    return arquivos_por_nome,datasets


def insere_novo_dataset(nome_dataset,api_key=api_key, address=address):
    """
    Faz uma requisição POST para criar um novo dataset na API.
    Retorna o ID do dataset criado ou None em caso de erro.
    """

    url = f"http://{address}:{port_ds}/api/v1/datasets"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "name": nome_dataset  # Nome do dataset será a chave faltante
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Levanta um erro se a requisição falhar

        dataset_info = response.json()
        # print(dataset_info)
        dataset_id = dataset_info["data"].get("id")  # Pegamos o ID do dataset criado

        # print(f"✅ Dataset '{nome_dataset}' criado com sucesso! ID: {dataset_id}")
        return dataset_id

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao criar o dataset '{nome_dataset}': {e}")
        return None

def insere_files(dataset_id, categoria, arquivos, api_key, address):
    """
    Faz upload de arquivos diretamente para um dataset na API.

    Parâmetros:
    - dataset_id: str -> ID do dataset onde os arquivos serão inseridos.
    - categoria: str -> Nome da categoria/pasta onde os arquivos estão armazenados.
    - arquivos: list[str] -> Lista de nomes de arquivos a serem enviados.
    - api_key: str -> Chave de autenticação para a API.
    - address: str -> Endereço do servidor API (ex.: "192.168.0.34").

    Retorno:
    - None. Exibe mensagens de sucesso ou erro conforme o status da requisição.
    """
    
    # Definir a URL do endpoint correto
    url = f"http://{address}:{port_ds}/api/v1/datasets/{dataset_id}/documents"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Lista para armazenar os arquivos a serem enviados
    files = []

    try:
        # Verificar e adicionar os arquivos na lista para multipart/form-data
        for arquivo in arquivos:
            caminho_completo = os.path.join('downloads', categoria, arquivo)
            print(f"\n\nCAMINHO COMPLETO: {caminho_completo}")
            if not os.path.exists(caminho_completo):
                print(f"⚠️ Arquivo não encontrado: {caminho_completo}")
                continue

            # Adicionar o arquivo para upload
            files.append(("file", (arquivo, open(caminho_completo, "rb"))))

        # Se nenhum arquivo válido for encontrado, aborta o upload
        if not files:
            print(f"⚠️ Nenhum arquivo válido encontrado na categoria '{categoria}'.")
            return

        # Enviar os arquivos via POST
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()

        print(f"✅ Upload concluído! {len(files)} arquivos enviados para o dataset {dataset_id}.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao fazer upload para o dataset {dataset_id}: {e}")

    finally:
        # Fechar todos os arquivos abertos para evitar vazamento de memória
        for _, file_obj in files:
            file_obj[1].close()
