import requests
import os
import json
import requests
import openai
from exa_py import Exa
openai.api_type = "azure"
openai.api_base = "https://ocp-chatocp.openai.azure.com/" 
openai.api_key = "9f7a3e99b44d49948d86949b1e450d45" 
openai.api_version = "2023-09-15-preview"
deployment_name = 'chatocp'

exa = Exa("20ba765f-c6d9-409d-9d99-2ac46b287c35")

def agenteAcciones(acciones_usuario):

    informacionStocks = []

    acciones = json.loads(obtenerAccionesTecnologicas(acciones_usuario))
    for accion in acciones['acciones_tecnologicas_recomendadas']:
        print(accion["ticker"] + ' - ' + accion["nombre"])
            
        # Obtener noticias
        responseNoticias = exa.search(
        "last news on" + accion["ticker"] + "stock from" + accion["nombre"],
        num_results=2,
        start_crawl_date="2023-01-14",
        start_published_date="2023-01-14",
        use_autoprompt=True
        )

        searchQueryIds = []
        print("\nNoticias: ")
        for noticia in responseNoticias.results:
            searchQueryIds.append(noticia.id)
            print(noticia.title)

        text = {"include_html_tags": False}
        highlights = None
        noticiasContent = exa.get_contents(
            searchQueryIds[:-1],
            text=text,
            highlights=highlights
        )

        stocksNoticias = []
        for content in noticiasContent.results:
            stocksNoticias.append(content.text)


        informacionStocks.append({
            "ticker": accion["ticker"],
            "nombre": accion["nombre"],
            "noticias": stocksNoticias
        })

    respuestaFinal = analizarAccionesTecnologicas(informacionStocks)

    print("\nRespuesta del agente:")
    print(respuestaFinal)

    return

# Conversacion con el chat para obtener las acciones tecnologicas en tendencia
def obtenerAccionesTecnologicas(acciones_usuario) : 
    response = openai.ChatCompletion.create(
        engine=deployment_name, 
        messages=[
            {"role": "system", "content": "Eres un experto en acciones de la bolsa, especificamente acciones de tecnologia. Quieres hacer proyecciones de las acciones en tecnologia y tambien proveer consejos para un inversionista"},
            {"role": "user", "content": "Brindame en un formato JSON la respuesta en formato JSON como este: {'acciones_tecnologicas_recomendadas': [{'nombre': 'Apple Inc.','ticker': 'AAPL','proyeccion_anual': 'Alta'}] de las sigiientes acciones separadas por una coma cada uno " + acciones_usuario},
        ]
    )
    return response['choices'][0]['message']['content']

# Analizar las acciones tecnologicas con los datos brindados
def analizarAccionesTecnologicas(informacionAcciones) :
    messages=[
            {"role": "system", "content": "Eres un experto en acciones de la bolsa. Quieres hacer proyecciones de las acciones en tecnologia y tambien proveer consejos para un inversionista. Normalmente generas prediccion basadas en las ultimas noticias de las compañias."},
            {"role": "user", "content": "Hola, las ultimas noticias de algunas acciones del area de tecnologia. Quiero que basada en esta informacion me generes un resumen de las ultimas noticias de las acciones para poder tomar una decision de inversion."},
            {"role": "assistant", "content": "Si, te ayudare a crear un resumen extenso de las noticias."},
    ]
    
    for accion in informacionAcciones:
        messages.append({"role": "user", "content": str(accion)})


    response = openai.ChatCompletion.create(
        engine=deployment_name, 
        messages=messages
    )
    return response['choices'][0]['message']['content']

def web_scrapper():
    print("Bienvenido al agente de acciones tecnológicas")
    acciones_usuario = input("Por favor menciona qué acciones te gustaría analizar separándolas por una coma. Ejemplo: Apple,Microsoft,Google: ")
    agenteAcciones(acciones_usuario)