# Utilizar uma imagem oficial do Python
FROM python:3.12
# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo requirements.txt para o container
COPY requirements.txt .

# Instalar as dependências necessárias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o conteúdo do diretório atual para o diretório /app do container
COPY . .

# Definir as variáveis de ambiente do arquivo .env
RUN python -m pip install python-dotenv

# Comando para rodar o script Python quando o container iniciar
CMD ["python", "crawler_SCORJ.py"]
