import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# URL do arquivo CSV
url = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"

def process_csv():
    # Baixar o arquivo CSV
    response = requests.get(url)
    csv_content = StringIO(response.text)
    
    # Ler o CSV com pandas
    df = pd.read_csv(csv_content, sep=';', decimal=',', thousands='.')
    
    # Converter as colunas de data para o formato datetime
    df['Data Vencimento'] = pd.to_datetime(df['Data Vencimento'], format='%d/%m/%Y')
    df['Data Base'] = pd.to_datetime(df['Data Base'], format='%d/%m/%Y')
    
    # Filtrar por títulos específicos e data de vencimento
    titulos_interesse = [
        ('Tesouro Selic', '01/03/2026'),
        ('Tesouro Selic', '01/03/2027'),
        ('Tesouro IPCA+', '15/05/2035'),
        ('Tesouro IPCA+', '15/05/2029'),
        ('Tesouro IPCA+', '15/08/2040'),
        ('Tesouro Prefixado', '01/01/2029'),
        # Adicione outros títulos e datas de vencimento conforme necessário
    ]
    
    df_filtrado = df[df.apply(lambda row: any((row['Tipo Titulo'] == titulo and 
                                               row['Data Vencimento'].strftime('%d/%m/%Y') == data_vencimento)
                                              for titulo, data_vencimento in titulos_interesse), axis=1)]
    
    # Manter apenas os dados mais recentes em relação à data base
    df_filtrado = df_filtrado.sort_values('Data Base', ascending=False).drop_duplicates(subset=['Tipo Titulo', 'Data Vencimento'], keep='first')
    
    # Selecionar apenas as colunas desejadas
    colunas_desejadas = ['Data Base', 'Tipo Titulo', 'Data Vencimento', 'Taxa Compra Manha', 'Taxa Venda Manha', 'PU Compra Manha', 'PU Venda Manha']
    df_final = df_filtrado[colunas_desejadas]
    
    # Ordenar por Tipo Titulo e Data Base
    df_final = df_final.sort_values(['Tipo Titulo', 'Data Vencimento', 'Data Base'], ascending=[True, True, False])
    
    # Gerar nome do arquivo de saída
    nome_arquivo = 'tesouro_direto_filtrado.csv'
    
    # Salvar o DataFrame filtrado como CSV
    df_final.to_csv(nome_arquivo, index=False, sep=';', decimal=',', date_format='%d/%m/%Y')
    
    print(f"Arquivo '{nome_arquivo}' criado com sucesso!")

if __name__ == "__main__":
    process_csv()