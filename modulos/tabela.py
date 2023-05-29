import re

class Tabela:
    def __init__(self,):
        self.create_table_columns = [
        "NU_PROCESSO_SEI VARCHAR(MAX)",
        "NM_RAZAO_SOCIAL VARCHAR(MAX)",
        "NU_CPF_CNPJ VARCHAR(MAX)",
        "DOC_FISCAL VARCHAR(MAX)",
        "TX_LINK_SEI_DOC_FISCAL VARCHAR(MAX)",
        "DT_EMISSAO VARCHAR(MAX)",
        "DT_ATESTO VARCHAR(MAX)",
        "DT_VENCIMENTO VARCHAR(MAX)",
        "VL_TOTAL VARCHAR(MAX)",
        "VALOR_ORIGINAL VARCHAR(MAX)",
        "JUROS_MULTA VARCHAR(MAX)",
        "DT_PGTO VARCHAR(MAX)",
        "DT_RECBTO VARCHAR(MAX)",
        "LOTE VARCHAR(MAX)",
        "TX_LINK_SEI_COMPROVANTE VARCHAR(MAX)",
        "NM_MODALIDADE_CONTRATUAL VARCHAR(MAX)",
        "NU_INSTRUMENTO_CONTRATUAL VARCHAR(MAX)",
        "TX_HISTORICO_DESPESA VARCHAR(MAX)",
        "NM_GRUPO VARCHAR(MAX)",
        "NM_PLANO_CONTAS VARCHAR(MAX)",
        "NM_UNIDADE VARCHAR(MAX)",
        "DS_OBSERVACAO_PENDENCIA VARCHAR(MAX)",
        "[COVID-19] VARCHAR(MAX)"
    ]
        self.table_columns = [
        'NU_PROCESSO_SEI',
        'NM_RAZAO_SOCIAL',
        'NU_CPF_CNPJ',
        'DOC_FISCAL',
        'TX_LINK_SEI_DOC_FISCAL',
        'DT_EMISSAO',
        'DT_ATESTO',
        'DT_VENCIMENTO',
        'VL_TOTAL',
        'VALOR_ORIGINAL',
        'JUROS_MULTA',
        'DT_PGTO',
        'DT_RECBTO',
        'LOTE',
        'TX_LINK_SEI_COMPROVANTE',
        'NM_MODALIDADE_CONTRATUAL',
        'NU_INSTRUMENTO_CONTRATUAL',
        'TX_HISTORICO_DESPESA',
        'NM_GRUPO',
        'NM_PLANO_CONTAS',
        'NM_UNIDADE',
        'DS_OBSERVACAO_PENDENCIA',
        '[COVID-19]'
    ]

 
    def clean_rows_columns(self, df, name_table):

        new_cols = {
            'NU_PROCESSO_SEI': ['Nº Processo SEI', 'N° Processo SEI'],
            'NM_RAZAO_SOCIAL': ['Razão Social', 'Razo Social', 'Raz?o Social', 'FORNECEDOR', 'RAZ?O SOCIAL'],
            'NU_CPF_CNPJ': ['CNPJ/CPF', 'CNPJ'],
            'DOC_FISCAL': ['NF-e', 'DOCTO FISCAL', 'Docto Fiscal', 'DOCTO. FISCAL', 'NFE', 'NFe', ' DOC. FISCAL'],
            'TX_LINK_SEI_DOC_FISCAL': ['Link', 'Link SEI do Docto. Fiscal', 'Link SEI do Docto. Fiscal'],
            'DT_EMISSAO': ['Dt. Emisso', 'Emissão', 'Dt. Emiss?o', 'DATA EMISÃO OU ATESTE', 'Dt. Emissão', 'DT. EMISS?O'],
            'DT_ATESTO': ['Atesto', 'Dt Atesto'],
            'DT_VENCIMENTO': ['Vencimento', 'Data de Vecto', 'DT de Vencimento'],
            'VL_TOTAL': ['Valor', 'Valor Total', 'VALOR'],
            'VALOR_ORIGINAL': ['Valor Original'],
            'JUROS_MULTA': ['Juros e Multa'],
            'DT_PGTO': ['Pagamento', 'Dt. Pagto', 'DATA PGTO', 'DT Pagamento'],
            'DT_RECBTO': ['Data Recbto'],
            'LOTE': ['Lote', 'LOTE', 'FORMA DE PAGTO', 'FORMA DE PAGAMENTO'],
            'TX_LINK_SEI_COMPROVANTE': ['Link SEI do Comprovante', 'Comprovante'],
            'NM_MODALIDADE_CONTRATUAL': ['Modalidade Contratual', 'Modalidade'],
            'NU_INSTRUMENTO_CONTRATUAL': ['Nº Instrumento', 'N? Instrumento Contratual', 'N¼ Instrumento Contratual', 'NM Instrumento', 'Nº INSTRUMENTO CONTRATUAL'],
            'TX_HISTORICO_DESPESA': ['Histórico da Despesa', 'Hist?rico da Despesa', 'HISTÓRICO DA DESPESA', 'Historico da Despesa'],
            'NM_GRUPO': ['Grupo'],
            'NM_PLANO_CONTAS': ['Plano de Contas'],
            'NM_UNIDADE': ['Unidade', 'Un. Saúde'],
            'DS_OBSERVACAO_PENDENCIA': ['Observa??o / Pend?ncia', 'Observação / Pendência', 'OBSERVAÇÕES', 'Observacao e Pendencia', 'OBSERVA??O / PEND?NCIA'],
            'COVID-19': ['COVID-19'],
        }

        # Criar dicionário de novos nomes para as colunas do dataframe
        new_names = {}
        try:
            for col in df.columns:
                for new_col, variations in new_cols.items():
                    pattern = r'\b(?:' + '|'.join(map(re.escape, variations)) + r')\b'
                    if re.fullmatch(pattern, col, re.IGNORECASE):
                        new_names[col] = new_col.upper()
                        break
                else:
                    new_names[col] = col.upper()
            df = df.rename(columns=new_names)
            df = df.replace(';', ' ', regex=True)
            cols_to_keep = [col for col in df.columns if col in new_cols]
            df = df[cols_to_keep]
            # Verificar se as novas colunas existem no dataframe
            for new_col in new_cols.keys():
                if new_col.upper() not in df.columns:
                    # Criar a nova coluna com o valor None
                    df = df.assign(**{new_col.upper(): None})
            df = df.dropna(how='all')
            # Substituir valores nulos restantes por "NULL"
            df = df.fillna('')
        except Exception as e:
            print(f'Erro ao tratar dados da {name_table}',e)
        return df


    def create_values_list(self, df):
        # Crie uma lista de tuplas contendo os valores de cada linha do DataFrame
        values = [tuple(row) for _, row in df.iterrows()]
        return values