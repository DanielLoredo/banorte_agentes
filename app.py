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

def agenteAcciones():

    informacionStocks = []

    acciones = json.loads(obtenerAccionesTecnologicas())
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


        # Obtencion de los datos de las acciones 
        # Precio de acciones mensual de 2023 y 2024
        # urlDataBursatil = "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=" + accion["ticker"] + "&apikey=YKXFH09TO2U3VZF3"
        urlDataBursatil = "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=" + accion["ticker"] + "&apikey=HHR6L6ZQ3BH9SPEI"
        lastData = requests.get(urlDataBursatil)
        datosBursatiles = json.loads(lastData.text)

        filtered_records = {date: record for date, record in datosBursatiles["Monthly Time Series"].items() if date.startswith("2023") or date.startswith("2024") or date.startswith("2022")}
        extracted_data = {}
        for date, values in filtered_records.items():
            extracted_data[date] = {'1. open': values['1. open'], '5. volume': values['5. volume']}
        # extracted_data = {'2024-03-13': {'1. open': '179.5500', '5. volume': '637249143'}, '2024-02-29': {'1. open': '183.9850', '5. volume': '1161711745'}, '2024-01-31': {'1. open': '187.1500', '5. volume': '1187139861'}, '2023-12-29': {'1. open': '190.3300', '5. volume': '1062317718'}, '2023-11-30': {'1. open': '171.0000', '5. volume': '1099760711'}, '2023-10-31': {'1. open': '171.2200', '5. volume': '1172845791'}, '2023-09-29': {'1. open': '189.4850', '5. volume': '1337873796'}, '2023-08-31': {'1. open': '196.2350', '5. volume': '1323817340'}, '2023-07-31': {'1. open': '193.7800', '5. volume': '996368613'}, '2023-06-30': {'1. open': '177.7000', '5. volume': '1297863403'}, '2023-05-31': {'1. open': '169.2800', '5. volume': '1275052503'}, '2023-04-28': {'1. open': '164.2700', '5. volume': '967580718'}, '2023-03-31': {'1. open': '146.8300', '5. volume': '1520461315'}, '2023-02-28': {'1. open': '143.9700', '5. volume': '1307294493'}, '2023-01-31': {'1. open': '130.2800', '5. volume': '1443652725'}}
        
        print("Datos históricos: ")
        print(extracted_data)

        informacionStocks.append({
            "ticker": accion["ticker"],
            "nombre": accion["nombre"],
            "historico": extracted_data,
            "noticias": stocksNoticias
        })

    respuestaFinal = analizarAccionesTecnologicas(informacionStocks)

    print("\nRespuesta del agente:")
    print(respuestaFinal)

    return

# Conversacion con el chat para obtener las acciones tecnologicas en tendencia
def obtenerAccionesTecnologicas() : 
    response = openai.ChatCompletion.create(
        engine=deployment_name, 
        messages=[
            {"role": "system", "content": "Eres un experto en acciones de la bolsa, especificamente acciones de tecnologia. Quieres hacer proyecciones de las acciones en tecnologia y tambien proveer consejos para un inversionista"},
            {"role": "user", "content": "Brindame en un formato JSON las 3 acciones de tecnologia que recomendarias de acuerdo a las proyecciones de anos pasados. Regresame la respuesta en formato JSON como este: {'acciones_tecnologicas_recomendadas': [{'nombre': 'Apple Inc.','ticker': 'AAPL','proyeccion_anual': 'Alta'}]"},
        ]
    )
    return response['choices'][0]['message']['content']

# Analizar las acciones tecnologicas con los datos brindados
def analizarAccionesTecnologicas(informacionAcciones) :
    messages=[
            {"role": "system", "content": "Eres un experto en acciones de la bolsa, especificamente acciones de tecnologia. Quieres hacer proyecciones de las acciones en tecnologia y tambien proveer consejos para un inversionista. Normalmente generas prediccion basadas en las ultimas noticias de las compañias especificas, rendimiento, datos historicos y otras variables."},
            {"role": "user", "content": "Hola, el dia de hoy voy a compartirte los datos historicos y ultimas noticias de algunas acciones del area de tecnologia. Quiero que basada en esta informacion me generes un consejo sobre cual accion deberia invertir, con razones basadas en hechos, datos historicos y una justificacion del porque si o porque no deberia invertir en cada una. Ademas de los datos que te estoy brindando, sientete libre de usar otra informacion que tengas a la mano o tengas acceso. Ademas, quiero que des tu opinion de cual compañia puede llegar a tener mayor crecimiento en este año, y que proveas una comparación historica del precio de las acciones de los años pasados. Incluye cifras del precio y porcentajes en la respuesta. La informacion esta hecha en formato de un objeto y es la siguiente:"},
            {"role": "assistant", "content": "Si, te ayudare a crear una proyeccion de inversion e incluire datos y porcentajes historicos que me compartiste."},
    ]
    
    for accion in informacionAcciones:
        messages.append({"role": "user", "content": str(accion)})


    response = openai.ChatCompletion.create(
        engine=deployment_name, 
        messages=messages
    )
    return response['choices'][0]['message']['content']

agenteAcciones()