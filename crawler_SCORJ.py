
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# URL do endpoint
url = "http://www2.rio.rj.gov.br/sco/resultservsco.cfm"  # Substitua pelo URL do endpoint

# Headers especificando que o conteúdo é x-www-form-urlencoded
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Lista de categorias a serem pesquisadas
categorias = ["AD", "AL", "AP", "BP", "CE", "CI", "CO", "DR", "EQ"]

# Dicionário para armazenar os dados de todas as categorias
dados_completos = {}

# Loop pelas categorias
for categoria in categorias:
    # Lista para armazenar os dados de todas as páginas para esta categoria
    dados_categoria = []

    # Iniciar a página como 1
    page_num = 1
    while True:
        # Payload com os parâmetros da requisição
        payload = {
            "pagina": page_num,
            "fgv_ref": "202405",
            "categoria": categoria,
            "fgvserv_descr": "",
            "filtrodescr": "",
            "coditemsco": "",
            "FGVParaSCO": "",
            "RealizaPesqServ": ""
        }

        # Fazer a requisição POST
        response = requests.post(url, data=payload, headers=headers)

        # Verificar o status da resposta
        if response.status_code == 200:
            # Parsear o HTML com BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontrar todas as tabelas no HTML
            tables = soup.find_all('table')

            # Verificar se há tabelas na página
            if tables:
                # Processar cada tabela
                for idx, table in enumerate(tables):
                    # Criar uma lista para armazenar os dados
                    data = []

                    # Extrair as linhas da tabela
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        cols = [ele.get_text(strip=True) for ele in cols]
                        if cols:
                            data.append(cols)

                    # Ajustar o número de colunas dinamicamente
                    if data:
                        num_columns = max(len(row) for row in data)
                        columns = [f"Coluna {i+1}" for i in range(num_columns)]

                        # Criar um DataFrame do pandas a partir dos dados
                        df = pd.DataFrame(data, columns=columns)

                        # Adicionar os dados da tabela ao lista da categoria atual
                        dados_categoria.append(df)

            else:
                print(f"Nenhuma tabela encontrada na página {page_num} com a categoria {categoria}")

            # Verificar se há próxima página
            next_page = soup.find('input', {'name': 'next'})
            if not next_page:
                break
            else:
                # Incrementar o número da página
                page_num += 1

        else:
            print(f"Erro na requisição para a página {page_num} com a categoria {categoria}: {response.status_code}")
            break

    # Concatenar todos os DataFrames da categoria em um único DataFrame
    if dados_categoria:
        dados_completos[categoria] = pd.concat(dados_categoria, ignore_index=True)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Parâmetros de conexão obtidos do arquivo .env
usuario = os.getenv('DB_USER')
senha = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')
porta = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')

# Criar a string de conexão
engine = create_engine(f'postgresql://{usuario}:{senha}@{host}:{porta}/{dbname}')

# Função para criar a tabela
def criar_tabela(nome_tabela):
    with engine.connect() as conexao:
        comando_criar_tabela = f"""
        CREATE TABLE IF NOT EXISTS {nome_tabela} (
            "Item de Serviço" TEXT,
            "Descrição" TEXT,
            "Und. de Medida" TEXT,
            "Custo R$" NUMERIC
        );
        """
        conexao.execute(text(comando_criar_tabela))
        print(f"Tabela {nome_tabela} criada ou já existente.")

# Exemplo de dados_completos (substitua pela sua variável real)
# dados_completos = {'categoria1': df1, 'categoria2': df2, ...}

for categoria, df in dados_completos.items():
    nome_tabela = f'dados_{categoria}'
    
    # Salvar os dados no banco de dados
    df.to_sql(nome_tabela, engine, index=False, if_exists='replace')
    print(f"Dados da categoria {categoria} salvos na tabela {nome_tabela}")

print("Processo concluído.")

