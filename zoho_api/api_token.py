import json
import requests
from time import sleep

def token(dados):
    url_refresh = (
        "https://accounts.zoho.com/oauth/v2/token?refresh_token={}&client_id={}&client_secret={}&grant_type=refresh_token"
    ).format(dados["chaveAtualizacao"], dados["idCliente"], dados["segredoCliente"])
    
    try:
        req = requests.post(url_refresh)
        req.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
        js = req.json()
        sleep(1)
        token = js["access_token"]
        print("Token atualizado!\n")
        dados["chaveAPI"] = token
    except requests.RequestException as e:
        print(f"Erro ao atualizar o token: {e}")
    
    return dados

def atualizar_token(caminho_json, dados):
    jsonAlterado = token(dados)
    with open(caminho_json, "w") as editFile:  # Usando gerenciador de contexto
        json.dump(jsonAlterado, editFile)  # Usando json.dump diretamente
    return dados