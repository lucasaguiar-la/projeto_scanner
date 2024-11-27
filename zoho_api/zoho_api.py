import os
import json
import twain
import requests
import http.client
import config
import mimetypes
import sys

from buscador.buscador import modal_escolha
from config import caminho_nova_pasta, pastaArquivos, inicioNomeArquivo, max_retries, loop
from utils.utils import verificar_criar_diretorio
from zoho_api.api_token import atualizar_token
from logger.logger import escrever_log

# Função para criar um registro no Zoho
def criarRegistro_zoho(arquivos):
    escrever_log("", level='info')
    escrever_log("===============================================", level='info')
    escrever_log("Inicializando a função 'criarRegistro_zoho'", level='info')

    # Verifica se o script está sendo executado como um executável
    if getattr(sys, 'frozen', False):
        caminho_dados = os.path.join(os.path.dirname(sys.executable), "..", "data", "dados.json")
    else:
        caminho_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dados.json")

    escrever_log(f"Caminho do arquivo de dados: {caminho_dados}", level='info')

    #[ATUALIZAÇÃO DO TOKEN]
    escrever_log("Lendo dados de autenticação do token...", level='info')
    caminho_token = ("./dados.json")
    with open(caminho_dados, "r") as readFile:
        dados = json.load(readFile)
        atualizar_token(caminho_token, dados)
    #[ATUALIZAÇÃO DO TOKEN]

    #🔸[ID PAI DEFINIDO PELO PDC]🔸
    modal_escolha(dados)
    idPai = config.id_pai_global
    if not idPai:
        escrever_log(f"Sem ID pai", level='error')
        print(idPai)
        raise Exception(f"Sem ID pai: {idPai}")

    escrever_log(f"ID do Pai: {idPai}", level='info')

    # Envio de arquivos
    if arquivos is not None:
        escrever_log(f"Iniciando envio de {len(arquivos)} arquivo(s)...", level='info')
        for loopCont, arquivo in enumerate(arquivos, start=1):
            try:
                with open(arquivo.name, 'rb') as file:
                    escrever_log(f"Enviando arquivo {loopCont} de {len(arquivos)}: {arquivo.name}", level='info')
                    callbackAfter_Computador(idPai, file, loopCont)
            except Exception as e:
                escrever_log(f"Erro ao enviar o arquivo {arquivo.name}: {e}", level='error')
                continue

    else:
        escrever_log("Nenhum arquivo selecionado. Iniciando captura com scanner.", level='info')
        capturarArquivos_scanner(idPai)

# Função de callback após nome do arquivo
def callbackAfter_nomeArquivo(remaining):
    escrever_log("", level='info')
    escrever_log("===============================================", level='info')
    escrever_log("Inicializando a função 'callbackAfter_nomeArquivo'", level='info')

    idPai = config.id_pai_global
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    caminho_dados = os.path.join(caminho_script, "dados.json")
    
    try:
        # Carrega os dados do arquivo JSON
        escrever_log("Carregando Token de acesso...", level='info')
        with open(caminho_dados, "r") as readFile:
            dados = json.load(readFile)

        headers = {'Authorization': f"{dados['inicioChave']} {dados['chaveAPI']}"}
        payload = json.dumps({"data": {"PDC_Digital": f"{idPai}"}})
        nomeForm2 = config.FORM_FILHO
        appUri = config.API_URL
        nomeRelatorio = config.API_REL
        url_post = f"/api/v2/{appUri}/form/{nomeForm2}"
        conn = http.client.HTTPSConnection("creatorapp.zoho.com")

        # Faz a requisição para criar o registro no Zoho
        conn.request("POST", url_post, payload, headers)
        response = conn.getresponse()
        respFilho = json.loads(response.read())
        escrever_log(f"Resposta da API (Filho): {respFilho}", level='info')

        #🔸[Aqui ele pega o registro do subform (onde vai os anexos) e sobe o arquivo, registrando o idPai (ID do PDC) e carregando o documento da pasta nesse registro]
        if respFilho["code"] == 3000:
            id_filho = respFilho['data']['ID']
            escrever_log(f"Registro filho criado com sucesso. ID do Filho: {id_filho}", level='info')

            url_upload = f"https://creatorapp.zoho.com/api/v2/{appUri}/report/{nomeRelatorio}/{id_filho}/Arquivos/upload"
            files = {
                'file': (f'{config.inicioNomeArquivo}{str(loop.loop)}.jpg', open(f'{pastaArquivos}{inicioNomeArquivo}{str(loop.loop)}.jpg', 'rb'), 'image/jpeg')
            }

            escrever_log("Enviando arquivo para upload...", level='info')
            upload_response = requests.post(url_upload, headers=headers, files=files)
            escrever_log(f"Arquivo enviado com sucesso. Resposta: {upload_response.text}", level='info')

        else:
            escrever_log(f"Erro na criação do registro filho. Código: {respFilho['code']}, Mensagem: {respFilho.get('message', 'Sem mensagem')}", level='error')
    
    except (json.JSONDecodeError, requests.RequestException, FileNotFoundError) as e:
        escrever_log(f"Erro: {e}", level='error')

    except Exception as e:
        escrever_log(f"Erro inesperado: {e}", level='error')

    finally:
        escrever_log("/===============================================/", level='info')
        return remaining

# Função de callback após o upload do arquivo
def callbackAfter_Computador(idPai, arquivos, loopCont):
    global upload_count, total_uploads
    escrever_log("", level='info')
    escrever_log("===============================================", level='info')
    escrever_log("Inicializando a função 'callbackAfter_Computador'", level='info')

    caminho_script = os.path.dirname(os.path.abspath(__file__))  # Caminho do script
    caminho_dados = os.path.join(caminho_script, "dados.json")  # Caminho do arquivo de dados

    try:
        # Carrega os dados do arquivo JSON
        escrever_log("Carregando arquivo de dados JSON...", level='info')
        with open(caminho_dados, "r") as readFile:
            dados = json.load(readFile)

        appUri = config.API_URL
        headers = {'Authorization': f"{dados['inicioChave']} {dados['chaveAPI']}"}
        payload = json.dumps({"data": {"PDC_Digital": f"{idPai}"}})
        nomeForm2 = config.FORM_FILHO
        nomeRelatorio = config.API_REL
        url_post = f"/api/v2/{appUri}/form/{nomeForm2}"
        conn = http.client.HTTPSConnection("creatorapp.zoho.com")

        # Implementa retries para a criação do registro e upload
        max_retries = 3

        for retries in range(max_retries):
            try:
                # Faz a requisição para criar o registro filho
                escrever_log(f"Tentativa {retries + 1}/{max_retries} de criação do registro filho...", level='info')
                conn.request("POST", url_post, payload, headers)
                response = conn.getresponse()
                respFilho = json.loads(response.read())

                escrever_log(f"Resposta da API (Filho): {respFilho}", level='info')

                #🔸[Aqui ele pega o registro do subform (onde vai os anexos) e sobe o arquivo, registrando o idPai (ID do PDC) e carregando o documento da pasta nesse registro]🔸
                if respFilho["code"] == 3000:
                    id_filho = respFilho['data']['ID']
                    escrever_log(f"Registro filho criado com sucesso. ID do Filho: {id_filho}", level='info')

                    # Determina o tipo do arquivo e a extensão correta
                    tipoArquivo, _ = mimetypes.guess_type(arquivos.name)  # Obtém o tipo do arquivo
                    extensao = '.' + arquivos.name.split('.')[-1]  # Obtém a extensão do arquivo
                    url_upload = f"https://creatorapp.zoho.com/api/v2/{appUri}/report/{nomeRelatorio}/{id_filho}/Arquivo/upload"  # URL para upload
                    files = {
                        'file': (f'{inicioNomeArquivo}{str(loopCont)}{extensao}', arquivos, tipoArquivo)  # Prepara o arquivo para upload
                    }

                    escrever_log("Enviando arquivo...", level='info')
                    # Faz o upload do arquivo
                    upload_response = requests.post(url_upload, headers=headers, files=files)
                    escrever_log(f"Arquivo enviado com sucesso. Resposta: {upload_response.text}", level='info')

                    # Incrementa o contador de uploads
                    upload_count += 1
                    escrever_log(f"Upload {upload_count}/{total_uploads} concluído", level='info')

                    break  # Sai do loop de retries se o registro e upload forem bem-sucedidos

                else:
                    escrever_log(f"Erro na criação do registro filho. Código: {respFilho['code']}, Mensagem: {respFilho.get('message', 'Sem mensagem')}", level='error')

            except Exception as e:
                # Loga exceção e incrementa o contador de tentativas
                escrever_log(f"Tentativa {retries + 1}/{max_retries} falhou com erro: {e}", level='error')
                if retries == max_retries - 1:
                    raise Exception(f"Erro após {max_retries} tentativas: {e}")

    except (json.JSONDecodeError, requests.RequestException, FileNotFoundError) as e:
        escrever_log(f"Erro: {e}", level='error')

    except Exception as e:
        escrever_log(f"Erro inesperado: {e}", level='error')

    finally:
        escrever_log("/===============================================/", level='info')

# Função de callback antes de nomear o arquivo
def callbackBefore_nomeArquivo(file_name=""):
    escrever_log("", level='info')
    escrever_log("===============================================", level='info')
    escrever_log("Inicializando a função 'callbackBefore_nomeArquivo'", level='info')

    loop.loop += 1

    if file_name:
        escrever_log(f"Preparando para salvar o arquivo: {file_name}", level='info')

    verificar_criar_diretorio(caminho_nova_pasta)

    # Caminho do arquivo a ser salvo
    caminho_arquivo = f"{pastaArquivos}{inicioNomeArquivo}{loop.loop}.jpg"

    for retries in range(max_retries):
        try:
            if not os.path.exists(pastaArquivos):
                escrever_log(f"Pasta {pastaArquivos} não encontrada. Tentativa {retries + 1}/{max_retries} de criar a pasta.", level='warning')
                os.makedirs(pastaArquivos)
                escrever_log(f"Pasta {pastaArquivos} criada com sucesso.", level='info')
            else:
                escrever_log(f"Pasta {pastaArquivos} já existente.", level='info')

            break  # Se o diretório for criado/verificado com sucesso, sair do loop

        except Exception as e:
            escrever_log(f"Erro ao criar a pasta {pastaArquivos}. Tentativa {retries + 1}/{max_retries} falhou com erro: {e}", level='error')
            if retries == max_retries - 1:
                raise Exception(f"Falha após {max_retries} tentativas de criar a pasta: {e}")

    escrever_log(f"Arquivo será salvo como: {caminho_arquivo}", level='info')

    return caminho_arquivo

# Função para capturar arquivos do scanner
def capturarArquivos_scanner(id_pai):
    escrever_log("", level='info')
    escrever_log("===============================================", level='info')
    escrever_log("Inicializando a função 'capturarArquivos_scanner'", level='info')
    escrever_log(f"ID Pai Global armazenado: {id_pai}", level='info')

    caminho_twain_dll = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "TWAINDSM.dll")
    
    try:
        # Adiciona o diretório da DLL do TWAIN
        escrever_log("Adicionando diretório da TWAINDSM.dll", level='info')
        os.add_dll_directory(os.path.dirname(caminho_twain_dll))
        
        # Inicializa o gerenciador TWAIN
        escrever_log("Inicializando o gerenciador TWAIN", level='info')
        tw = twain.SourceManager()  # Cria o gerenciador TWAIN
        
        # Abre a fonte do scanner
        escrever_log("Abrindo a fonte do scanner", level='info')
        src = tw.open_source()  # Abre a fonte do scanner
        
        if src:
            escrever_log("Fonte do scanner aberta, iniciando aquisição", level='info')

            try:
                # Inicia a aquisição de arquivos do scanner
                src.acquire_file(before=callbackBefore_nomeArquivo, after=callbackAfter_nomeArquivo, show_ui=False, modal=False)
                escrever_log("Aquisição de arquivo iniciada com sucesso", level='info')

            except Exception as e:
                escrever_log(f"Erro durante a aquisição do arquivo: {e}", level='error')
                raise
            
            # Define a URL com o id_pai para abrir no navegador
            url = f"https://guillaumon.zohocreatorportal.com/#{config.FORM_FINAL}"
            escrever_log(f"URL gerada: {url}", level='info')

            escrever_log("Abrindo navegador com a URL gerada", level='info')
            # webbrowser.open(url)

        else:
            escrever_log("Nenhuma fonte de scanner disponível", level='warning')
            
    except FileNotFoundError as fnf_error:
        escrever_log(f"Erro de arquivo não encontrado: {fnf_error}", level='error')
        
    except Exception as e:
        escrever_log(f"Erro inesperado: {e}", level='error')
        raise

    finally:
        escrever_log("/===============================================/", level='info')