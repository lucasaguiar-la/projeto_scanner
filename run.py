import os
import json
import twain
import requests
import webbrowser 
import http.client 
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from threading import Thread, Event

caminho_documentos = Path(os.path.expanduser('~')) / 'Documents'

caminho_nova_pasta = caminho_documentos / 'Imagens do Scanner'

if not caminho_nova_pasta.exists():
    caminho_nova_pasta.mkdir()
    print(f'A pasta "{caminho_nova_pasta}" foi criada com sucesso.')
else:
    print(f'A pasta "{caminho_nova_pasta}" já existe.')

global pastaArquivos, inicioNomeArquivo, loop, dados, nomeForm, nomeRelatorio

pastaArquivos = str(caminho_nova_pasta) + "\\"
inicioNomeArquivo = "Documento"
conn = http.client.HTTPSConnection("creatorapp.zoho.com")
appUri = "<nome_usuário>/<nome_app>"
nomeForm = "<formulário>"
nomeRelatorio = "relatório"
nomeRelatorio2 ="relatório2"

def loading_page(event: Event):
    root = tk.Tk()
    def close_loading():
        if event.is_set():
            root.destroy()
        else:
            root.after(5000, close_loading)

    root.title("Carregando")
    root.geometry("300x200")
    root.resizable(False, False)

    # Menssagem de carregamento
    loading_label = ttk.Label(root, text="Carregando arquivos...", font=("Arial", 14))
    loading_label.pack(pady=50)

    # Barra de progresso
    progress_bar = ttk.Progressbar(root, length=200, mode='indeterminate')
    progress_bar.pack()

    # Determina que fechara depois de 5seg
    root.after(5000, close_loading)

    # Animação do carregamento
    progress_bar.start(10)
    root.mainloop()

loop = 0
def atualizar_token(ddsJson):
    url_refresh = "https://accounts.zoho.com/oauth/v2/token?refresh_token="+ ddsJson["chaveAtualizacao"] + "&client_id=" + ddsJson["idCliente"] +"&client_secret=" + ddsJson["segredoCliente"] + "&grant_type=refresh_token"
    req = requests.post(url_refresh)
    js = req.json()
    print(js)
    token = js["access_token"]
    ddsJson["chaveAPI"] = token
    return ddsJson
    
def criarRegistro_zoho():
    
    cvValida = False
    playWhile = True
    while cvValida == False:
        readFile = open("./_internal/app_scanner/dados.json", "r")
        dados = json.load(readFile)
        # Token de validação
        headers= {'Authorization': dados["inicioChave"] + " " + dados["chaveAPI"]}
        # Conteúdo do corpo da requisição
        payload = json.dumps({
        "data": {
            "workFlow": "Carregado via API"
        }
        })
        # Estabelece a conexão e faz a requisição com a API, o Token e o Corpo, criando um registro
        conn.request("POST", f"/api/v2/{appUri}/form/{nomeForm}", payload, headers)
        respPai = json.loads(conn.getresponse().read())
        print("Pai => ")
        print(respPai)
        if respPai["code"] == 3000:
            idPai = (respPai["data"]["ID"])
            #CRIAR UM REGISTRO PARA CADA DOCUMENTO#
            capturarArquivos_scanner(idPai)
                
            readFile.close()
            break
        elif respPai["code"] == 1030 or respPai["code"] == 2945:
            jsonAlterado = atualizar_token(dados)
            editFile = open("./_internal/app_scanner/dados.json", "w")
            editFile.write(json.dumps(jsonAlterado))
            readFile.close()
            editFile.close()
            continue

def callbackAfter_nomeArquivo(remaining, idPai):
    # Conteúdo do corpo da requisição
    readFile = open("./_internal/app_scanner/dados.json", "r")
    dados = json.load(readFile)
    # Token de validação
    headers= {'Authorization': dados["inicioChave"] + " " + dados["chaveAPI"]}
    payload = json.dumps({"data": {"campo": "nome_campo","nome_formulario" : f"{idPai}"}})
    ##
    nomeForm2 = "outro_formulario"
    conn.request("POST", f"/api/v2/{appUri}/form/{nomeForm2}", payload, headers)
    respFilho = json.loads(conn.getresponse().read())
    print("Filho => ")
    print(respFilho)
    if respFilho["code"] == 3000:
        id_filho = (respFilho['data']['ID'])

        #ADICIONA OS DOCUMENTOS
        url = f"https://creatorapp.zoho.com/api/v2/<usuario>/<nome_app>/report/{nomeRelatorio}/{id_filho}/Arquivo/upload"
        payload = {}
        files=[
        (
            'file',
            (f'{inicioNomeArquivo}{str(loop)}.jpg', open(f'{pastaArquivos}{inicioNomeArquivo}{str(loop)}.jpg','rb'),'image/jpeg')
        )
            ]
        # Manda a imagem no registro criado
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print(response.text)
    return remaining

def callbackBefore_nomeArquivo(infoImg):
    global loop
    loop += 1
    return f"{pastaArquivos}{inicioNomeArquivo}{loop}.jpg"

def capturarArquivos_scanner(id_pai):
    tw = twain.SourceManager()
    src = tw.open_source()
    if src:

        event = Event()
        new_thread = Thread(target=loading_page, args=(event,))
    
        new_thread.start()
        src.acquire_file(before=callbackBefore_nomeArquivo, after=callbackAfter_nomeArquivo,show_ui=False, modal=False, idPai=id_pai)
        wf = "editar_carregados_api"
        url = f"https://<usuario>.zohocreatorportal.com/#Form:{nomeForm}?recLinkID={id_pai}&workFlow={wf}&viewLinkName={nomeRelatorio2}"
        event.set()
        webbrowser.open(url)
criarRegistro_zoho()

