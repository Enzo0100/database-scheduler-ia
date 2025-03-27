import whisper
import os

def send_to_whisper(caminho_audio, modelo='tiny', idioma='pt'):
    """
    Função super simplificada para transcrição com Whisper
    - Deixa o próprio Whisper gerenciar o download e cache dos modelos
    - Trata apenas os erros essenciais
    """
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(caminho_audio):
            print("Arquivo de áudio não encontrado!")
            return None

        # Carrega o modelo (deixa o Whisper cuidar do download)
        print("Carregando modelo Whisper...")
        model = whisper.load_model(modelo)
        
        # Faz a transcrição
        print("Transcrevendo áudio...")
        resultado = model.transcribe(caminho_audio, language=idioma)
        
        return resultado['text']
    
    except Exception as e:
        print(f"Erro na transcrição: {str(e)}")
        return None