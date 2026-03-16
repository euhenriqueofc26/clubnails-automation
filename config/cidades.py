SAO_PAULO_CENTER = (-23.5505, -46.6333)

SAO_PAULO_GRID = {
    'nome': 'São Paulo',
    'lat_min': -23.7,
    'lat_max': -23.4,
    'lng_min': -46.8,
    'lng_max': -46.4,
    'step': 0.03
}

CIDADES_BRASIL = {
    'sao_paulo': {
        'nome': 'São Paulo',
        'lat_center': -23.5505,
        'lng_center': -46.6333,
        'lat_min': -23.7,
        'lat_max': -23.4,
        'lng_min': -46.8,
        'lng_max': -46.4,
        'step': 0.08
    },
    'rio_de_janeiro': {
        'nome': 'Rio de Janeiro',
        'lat_center': -22.9068,
        'lng_center': -43.1729,
        'lat_min': -23.0,
        'lat_max': -22.7,
        'lng_min': -43.5,
        'lng_max': -42.9,
        'step': 0.03
    },
    'belo_horizonte': {
        'nome': 'Belo Horizonte',
        'lat_center': -19.9167,
        'lng_center': -43.9345,
        'lat_min': -20.1,
        'lat_max': -19.7,
        'lng_min': -44.2,
        'lng_max': -43.7,
        'step': 0.025
    },
    'brasilia': {
        'nome': 'Brasília',
        'lat_center': -15.7975,
        'lng_center': -47.8919,
        'lat_min': -16.0,
        'lat_max': -15.5,
        'lng_min': -48.1,
        'lng_max': -47.7,
        'step': 0.025
    },
    'salvador': {
        'nome': 'Salvador',
        'lat_center': -12.9714,
        'lng_center': -38.5014,
        'lat_min': -13.2,
        'lat_max': -12.7,
        'lng_min': -38.7,
        'lng_max': -38.3,
        'step': 0.025
    },
    'curitiba': {
        'nome': 'Curitiba',
        'lat_center': -25.4284,
        'lng_center': -49.2733,
        'lat_min': -25.6,
        'lat_max': -25.2,
        'lng_min': -49.5,
        'lng_max': -49.0,
        'step': 0.025
    },
    'fortaleza': {
        'nome': 'Fortaleza',
        'lat_center': -3.7172,
        'lng_center': -38.5433,
        'lat_min': -3.9,
        'lat_max': -3.5,
        'lng_min': -38.8,
        'lng_max': -38.3,
        'step': 0.025
    },
    'recife': {
        'nome': 'Recife',
        'lat_center': -8.0476,
        'lng_center': -34.8770,
        'lat_min': -8.3,
        'lat_max': -7.8,
        'lng_min': -35.2,
        'lng_max': -34.8,
        'step': 0.025
    }
}

def get_cidade(cidade_key):
    return CIDADES_BRASIL.get(cidade_key, CIDADES_BRASIL['sao_paulo'])
