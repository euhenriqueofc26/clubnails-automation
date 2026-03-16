import math
from config.cidades import get_cidade
from utils.logger import log_info

def gerar_grid_coordenadas(cidade_key='sao_paulo', step=None):
    cidade = get_cidade(cidade_key)
    
    if step is None:
        step = cidade['step']
    
    coordenadas = []
    
    lat = cidade['lat_min']
    while lat <= cidade['lat_max']:
        lng = cidade['lng_min']
        while lng <= cidade['lng_max']:
            coordenadas.append({
                'lat': round(lat, 6),
                'lng': round(lng, 6)
            })
            lng += step
        lat += step
    
    log_info(f"Grid gerado para {cidade['nome']}: {len(coordenadas)} coordenadas")
    return coordenadas

def gerar_grid_baixo_step(cidade_key='sao_pao', step=0.015):
    cidade = get_cidade(cidade_key)
    
    coordenadas = []
    
    lat = cidade['lat_min']
    while lat <= cidade['lat_max']:
        lng = cidade['lng_min']
        while lng <= cidade['lng_max']:
            coordenadas.append({
                'lat': round(lat, 6),
                'lng': round(lng, 6)
            })
            lng += step
        lat += step
    
    return coordenadas

def calcular_distancia(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2)

def grid_para_teste():
    return [
        {'lat': -23.55, 'lng': -46.63},
        {'lat': -23.56, 'lng': -46.63},
        {'lat': -23.57, 'lng': -46.63},
        {'lat': -23.58, 'lng': -46.63},
        {'lat': -23.59, 'lng': -46.63},
    ]

if __name__ == '__main__':
    grid = gerar_grid_coordenadas('sao_paulo')
    print(f"Total de coordenadas: {len(grid)}")
    for i, coord in enumerate(grid[:5]):
        print(f"{i+1}: {coord}")
