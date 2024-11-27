import os
import json
import requests
import customtkinter
import config

def modal_escolha(dados):
    root = customtkinter.CTk()
    root.title("Scanner - PDC")
    root.geometry("570x200")
    root.resizable(False, False)
    root.geometry("+%d+%d" % (root.winfo_screenwidth() // 2 - root.winfo_reqwidth() // 2, root.winfo_screenheight() // 2 - root.winfo_reqheight() // 2))
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    mensagem = customtkinter.CTkLabel(root, font=("Montserrat" ,16), text="Digite o número do PDC dos arquivos que serão escaneados")
    mensagem.pack(pady=10)

    numero_pdc = customtkinter.CTkEntry(root, placeholder_text="Número do PDC")
    numero_pdc.pack(pady=10)

    # Botão para confirmar a escolha
    btn = customtkinter.CTkButton(root, text="Escanear arquivos", command=lambda: BuscaRegistros.buscar_pdc(root, mensagem, dados, numero_pdc.get()))
    btn.pack(pady=10)

    root.mainloop()


class BuscaRegistros:
    def buscar_pdc(root, mensagem, dados, numero_pdc):
        if (numero_pdc == '' or numero_pdc == ' ' or numero_pdc == None or numero_pdc == '0'):
            mensagem.configure(text="Digite um número de PDC válido.", text_color="red")
            return

        app = config.API_URL
        nome_relatorio = config.REL_PDC #🔸[REL DOS PDCs]🔸

        num_pdc = str(numero_pdc)
        filtro_docs = f"Numero_do_PDC={num_pdc}&Numero_do_PDC_op=26" #Contains

        api_url = (f"https://creatorapp.zoho.com/api/v2/{app}/report/{nome_relatorio}?{filtro_docs}")
        headers = {'Authorization': dados["inicioChave"] + " " + dados["chaveAPI"]}

        with requests.Session() as session:
            response = session.get(api_url, headers=headers)
            res_json = response.json()
            print("Resposta:", response.status_code)

            while True:
                if response.status_code == 200:
                    '''
                    # Salva a resposta da requisição em um arquivo JSON
                    with open("resposta_upload.json", "w") as arquivo_resposta:
                        json.dump(res_json, arquivo_resposta)
                    '''

                    id_registro = res_json["data"][0]["ID"]
                    print("[ID do registro]:", id_registro)

                    config.id_pai_global = id_registro

                    root.destroy()
                    return False

                else:
                    print("Nenhum registro encontrado.")
                    mensagem.configure(text="Número de PDC não encontrado, tente novamente.", text_color="yellow")
                    return

    def atualizar_registro(app, id_registro, headers, session):
        pasta_arquivos = "./testes_pdc/"
        form_filho = config.FORM_FILHO

        for arquivo in os.listdir(pasta_arquivos):
            #[POST]
            print("Criando registro p/ anexo...")
            url_post = (f"https://creatorapp.zoho.com/api/v2/{app}/form/{form_filho}")
            payload = json.dumps(
                {
                    "data": 
                    {
                        "PDC_Digital": f"{id_registro}"
                    }
                }
            )
            post_req = session.post(url_post, data=payload, headers=headers)
            post_resp_test = post_req.json()
            post_resp = json.loads(post_req.text)
            print("Post:", post_req.status_code)

            if post_req.status_code == 200:
                print("Registro atualizado com sucesso.")
                print(post_req.text + "\n")
                id_upload = post_resp_test["data"]["ID"]

                #[UPLOAD]
                nome_relatorio = "laranj_arquivos_pdc_Report"
                url_upload = (f"https://creatorapp.zoho.com/api/v2/{app}/report/{nome_relatorio}/{id_upload}/Arquivos/upload")

                if (arquivo == "." or arquivo == "..") or (os.path.isdir(f"{pasta_arquivos}{arquivo}")):
                    print("Pasta")
                    continue

                files = [
                    (
                        'file',
                        (
                            f'{arquivo}', open(f'{pasta_arquivos}{arquivo}', 'rb'), 'image/png'
                        )
                    )
                ]

                upload_response = session.post(url_upload, headers=headers, data={}, files=files)

                print("\nArquivo:", arquivo)
                print(f"ID: {id_registro} - Upload: {upload_response.status_code}\n{upload_response.text}")

#modal_escolha()
