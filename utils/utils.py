import os

# Função para verificar e criar diretórios
def verificar_criar_diretorio(caminho):
    if not caminho.exists():
        caminho.mkdir(parents=True)  # Cria a pasta
        print(f'A pasta "{caminho}" foi criada com sucesso.')
    else:
        print(f'A pasta "{caminho}" já existe.')