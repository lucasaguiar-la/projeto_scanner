import logging

# Configuração do logger
def configurar_logger(caminho_log):
    logging.basicConfig(
        filename=caminho_log,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# Função para registrar logs
def escrever_log(mensagem, level='info'):
    levels = {
        'info': logging.info,
        'warning': logging.warning,
        'error': logging.error,
        'critical': logging.critical
    }
    if level in levels:
        levels[level](mensagem)
    else:
        logging.info(mensagem)