from pathlib import Path
from datetime import datetime
from utils.utils import verificar_criar_diretorio
from logger.logger import configurar_logger, escrever_log
from zoho_api.zoho_api import criarRegistro_zoho

caminho_documentos = Path.home() / 'Documents'
caminho_logs = caminho_documentos / 'logs'
data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
nome_log = f"log_scanner_{data_atual}.txt"
caminho_log = caminho_logs / nome_log

verificar_criar_diretorio(caminho_logs)
configurar_logger(caminho_log)
escrever_log("Iniciando o sistema de scanner.")

criarRegistro_zoho(None)
