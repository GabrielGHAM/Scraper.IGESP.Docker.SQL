import re


def generate_name_table(link):
    year_table = re.findall(r'\d{4}', link.get('href'))[-1]
    return f'{link.text} de {year_table}'

def generate_filename(name_table):
    return name_table.replace(' ', '_').lower() + '.csv'

def formatar_tempo(tempo):
    tempo_arredondado = round(tempo, 2)  
    tempo_formatado = "%.2f segundos" % tempo_arredondado  
    return tempo_formatado

