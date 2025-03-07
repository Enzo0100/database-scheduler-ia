# Projeto: Scheduler de Atualização de Banco de Dados dos Agentes de IA

Este projeto implementa um agendador que atualiza a base de dados dos agentes de IA diariamente à meia-noite.

---

## 📌 Como Rodar o Projeto

### 🔹 Executando Localmente (Sem Docker)

1. **Criar um ambiente virtual**:
   ```sh
   python -m venv venv
   ```
2. **Ativar o ambiente virtual**:
   - Linux/macOS:
     ```sh
     source venv/bin/activate
     ```
   - Windows:
     ```sh
     venv\Scripts\activate
     ```
3. **Instalar as dependências**:
   ```sh
   pip install -r requirements.txt
   ```
4. **Executar o projeto**:
   ```sh
   python main.py
   ```

---

## 🚀 Rodando com Docker

### 🔹 Construindo e Rodando com Docker Manualmente

Caso queira rodar sem Docker Compose, siga os passos abaixo:

1. **Construir a imagem**:
   ```sh
   docker build -t ai_scheduler -f docker/Dockerfile .
   ```
2. **Executar o container**:
   ```sh
   docker run -d --name ai_scheduler ai_scheduler
   ```

Para parar e remover o container:
```sh
   docker stop ai_scheduler && docker rm ai_scheduler
```

🚨 **Importante:** O `Dockerfile` já copia `main.py` corretamente para dentro do container, então ele será executado automaticamente.

---

## 🌐 Deploy em Produção com Docker Swarm

Se estiver utilizando **Docker Swarm** para um ambiente de produção:

1. **Inicializar o Swarm (caso ainda não esteja ativo)**:
   ```sh
   docker swarm init
   ```
2. **Fazer o deploy do serviço**:
   ```sh
   docker stack deploy -c docker/docker-swarm.yml ai_scheduler
   ```
3. **Verificar se o serviço está rodando**:
   ```sh
   docker service ls
   ```
4. **Para remover o serviço**:
   ```sh
   docker stack rm ai_scheduler
   ```

---

## 🔄 Atualizando a Imagem e o Serviço

Se precisar atualizar a imagem em produção, siga os passos abaixo:

1. **Rebuild da imagem**:
   ```sh
   docker build -t ai_scheduler -f docker/Dockerfile .
   ```
2. **Fazer o deploy novamente**:
   ```sh
   docker stack deploy -c docker/docker-swarm.yml ai_scheduler
   ```
3. **Verificar a atualização**:
   ```sh
   docker service ps ai_scheduler
   ```

---

## ⌛ Agendamento com Cron no Linux

Para executar esse Docker automaticamente todos os dias à meia-noite:

1. **Editar o crontab**:
   ```sh
   crontab -e
   ```
2. **Adicionar a seguinte linha** para parar, reconstruir e rodar os containers diariamente às 00:00:
   ```
   0 0 * * * cd /caminho/para/seu/projeto && docker-compose down && docker-compose up --build -d
   ```
3. **Salvar e sair** (`CTRL+X`, `Y`, `Enter`).

Agora, o cron garantirá que o Docker seja executado automaticamente todos os dias à meia-noite.

---

## 🛠 Tecnologias Utilizadas

- **Python 3.12**
- **Docker & Docker Compose**
- **Docker Swarm (para produção)**

Se precisar de mais informações, fique à vontade para perguntar! 🚀