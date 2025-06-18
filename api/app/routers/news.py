from fastapi import APIRouter, Query, HTTPException
import os
import requests
import csv
from io import StringIO

# Creación del APIRouter para las noticias
router = APIRouter()

# Clave de API de Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')

@router.get('/news')
def get_news(topics: str = Query('technology'), time_from: str = Query(None), limit: int = Query(10, description="Número máximo de noticias a devolver")):
    """
    Endpoint para obtener noticias y sentimiento del mercado.
    """
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics={topics}&apikey={ALPHA_VANTAGE_API_KEY}'
    if time_from:
        url += f'&time_from={time_from}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'feed' not in data:
            return {'feed': []} # Devolver lista vacía si no hay noticias
        
        # Limitar el número de noticias si se ha especificado un límite
        if limit and 'feed' in data:
            data['feed'] = data['feed'][:limit]
            
        return data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f'Error al contactar la API de Alpha Vantage: {e}')
    except ValueError:
        raise HTTPException(status_code=500, detail='Error al decodificar la respuesta JSON de Alpha Vantage.')

@router.get('/economic_calendar')
def get_economic_calendar(horizon: str = Query('3month')):
    """
    Endpoint para obtener eventos del calendario económico desde un CSV y convertirlo a JSON.
    """
    url = f'https://www.alphavantage.co/query?function=ECONOMIC_CALENDAR&horizon={horizon}&apikey={ALPHA_VANTAGE_API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()

        # El contenido es CSV, lo procesamos
        csv_content = response.text
        csv_file = StringIO(csv_content)
        reader = csv.reader(csv_file)
        
        # Omitir la cabecera
        header = next(reader)
        
        # Crear una lista de diccionarios
        events = []
        for row in reader:
            event_data = {
                'event': row[0],
                'country': row[1],
                'date': row[2],
                'time': row[3],
                'impact': row[4],
                'forecast': row[5],
                'previous': row[6]
            }
            events.append(event_data)
            
        return {'events': events}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f'Error al contactar la API de Alpha Vantage: {e}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error al procesar los datos del calendario: {e}')
