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

def agentePrimas():
    informacionPrimas = {}

    # 1. Datos de las materias primas (commodities) ultimas
    urlDataPrimas = "https://api.databursatil.com/v1/commodities?token=2c14e8c675d45db75e05323b74abbd"
    dataPrimas = json.loads(requests.get(urlDataPrimas).text)

    informacionPrimas["Precio de las materias primas"] = dataPrimas["hidrocarburos"]
    
    print("Ultimos precios de primas: ")
    print(informacionPrimas)
    
    # 2. Noticias de inversion en materias primas
    responseNoticias = exa.search(
        "Last news on commidity investing",
        num_results=8,
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

    primasNoticias = []
    for content in noticiasContent.results:
        primasNoticias.append(content.text)

    informacionPrimas["noticias"] = primasNoticias

    respuestaFinal = analizarPrimas(informacionPrimas)

    print("\nRespuesta del agente:")
    print(respuestaFinal)

    return


# Analizar las acciones tecnologicas con los datos brindados
def analizarPrimas(informacionPrimas) :
    messages=[
            {"role": "system", "content": "Eres un experto en inversiones de primas tanto a nivel nacional como internaciones. Esto incluye inversiones en oro, plata, crudo, gasolina, etc. Normalmente das consejos y proyecciones de inversiones en primas, y tomas en cuenta datos historicos y principalmente noticias recientes, siempre manejandolo de manera analitica y usando datos o métricas recientes"},
            {"role": "user", "content": "Hola, el dia de hoy voy a compartirte los datos historicos y ultimas noticias sobre las inversiones en diferentes materias primas. Debes generar una recomendacion acerca de una o varias inversiones en primas, de las cuales tienes que justificar y brindar razones por las cuales si o no se deberia invertir en dicha prima. Puedes usar la informacion que yo te brindo y tambien conocimiento que ya tengas. Debes incluir datos numericos y preferiblemente porcentajes"},
            {"role": "assistant", "content": "Si, te ayudare a crear un consejo financiero acerca la inversion de primas, usare la información que me brindates y datos generales para crear un razonamiento sobre cual seria una buena opciónd de inversión"},
            {"role": "user", "content": str(informacionPrimas)}
    ]

    response = openai.ChatCompletion.create(
        engine=deployment_name, 
        messages=messages
    )
    return response['choices'][0]['message']['content']

agentePrimas()