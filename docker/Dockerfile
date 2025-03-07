FROM python:3.12

# Define o timezone como America/Sao_Paulo
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install ffmpeg and other dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*
    
# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o restante do projeto
COPY .. /app

# Instala as dependências diretamente no ambiente do container
RUN pip install -r requirements.txt


# Define o comando de execução padrão
CMD ["python3", "logic/main.py"]
