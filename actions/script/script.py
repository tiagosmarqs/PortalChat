import sqlite3
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

#define o nome do arquivo do banco de dados SQLite
db_file = 'actions/banco_de_dados/banco_de_dados.db'

url = 'https://portal.ufvjm.edu.br/servicos'

response = requests.get(url)


#verifica se a requisição foi realizada com sucesso
if response.status_code == 200:

    soup = BeautifulSoup(response.text, 'html.parser')

    #tenta se conectar ao banco de dados SQLite
    conn = sqlite3.connect(db_file)
    
    #cria um objeto cursor, que permite executar comandos SQL no banco de dados
    cursor = conn.cursor()
    
    #verifica se a tabela "servicos" já existe no banco de dados
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="servicos"')
    
    #recupera o resultado da verificação se a tabela existe
    table_exists = cursor.fetchone()


    if table_exists:
        #se a tabela "servicos" existir, verifica se a última inserção na tabela ocorreu há mais de 7 dias
        cursor.execute('SELECT data_insercao FROM servicos ORDER BY data_insercao DESC LIMIT 1')
        data_insercao = cursor.fetchone()

        #fecha a conexão com o banco de dados
        conn.close()
        
        #converte a data de inserção em um objeto datetime
        data_insercao = datetime.strptime(data_insercao[0], '%Y-%m-%d %H:%M:%S.%f')
            
        #se a última inserção tiver ocorrido há mais de 7 dias, apaga a tabela "servicos" e reinsere os dados
        if data_insercao < datetime.now() - timedelta(days=7):

            #lista para armazenar os dados a serem inseridos na tabela
            dados_servicos = []
                
            for div in soup.find_all('div', {'class': 'collection-item'}):
                #para cada div encontrada, salva o atributo "href" da tag "a" na variável "url_servico"
                url_servico = div.find('a')['href']
                #busca a página do serviço
                response = requests.get(url_servico)
                    
                soup = BeautifulSoup(response.text, 'html.parser')

                #busca a div com o id "category"
                div_category = soup.find("div", id="category")

                #verifica se a div foi encontrada
                if div_category:
                    #busca todas as tags "a" dentro da div
                    a_tags = div_category.find_all("a")

                    possui_conteudo = False

                    #percorre as tags "a" encontradas
                    for a in a_tags:
                        #salva na variável o conteúdo da tag "a"
                        conteudo = a.string

                        #verifica se o conteúdo está entre os valores desejados
                        if conteudo in ["Estudantes internos de ensino a distância", "Estudantes internos de graduação", "Estudantes internos de pós-graduação"]:
                            possui_conteudo = True
                        
                    if possui_conteudo==True:
    
                        titulo = soup.find('h1').text

                        dados_servicos.append((titulo, url_servico, datetime.now()))

            # tenta se conectar ao banco de dados SQLite
            conn = sqlite3.connect(db_file)

            # cria um objeto cursor, que permite executar comandos SQL no banco de dados
            cursor = conn.cursor()
            #apaga a tabela "servicos"
            cursor.execute('DROP TABLE IF EXISTS servicos')

            cursor.execute('CREATE TABLE servicos (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, url_servico TEXT, data_insercao DATETIME)')
            #insere os novos dados na tabela "servicos"
            cursor.executemany('INSERT INTO servicos (titulo, url_servico, data_insercao) VALUES (?, ?, ?)', dados_servicos)
            #commita as mudanças no banco de dados
            conn.commit()
            #fecha a conexão com o banco de dados
            conn.close()
    else:

        #fecha a conexão com o banco de dados
        conn.close()
        #lista para armazenar os dados a serem inseridos na tabela
        dados_servicos = []                
                
        for div in soup.find_all('div', {'class': 'collection-item'}):
            #para cada div encontrada, salva o atributo "href" da tag "a" na variavel "url_servico"
            url_servico = div.find('a')['href']
            #busca a página do serviço
            response = requests.get(url_servico)
                    
            soup = BeautifulSoup(response.text, 'html.parser')
            #busca a div com o id "category"
            div_category = soup.find("div", id="category")

            #verifica se a div foi encontrada
            if div_category:
                #busca todas as tags "a" dentro da div
                a_tags = div_category.find_all("a")

                possui_conteudo = False

                #percorre as tags "a" encontradas
                for a in a_tags:
                    #salva na variável o conteúdo da tag "a"
                    conteudo = a.string

                    #verifica se o conteúdo está entre os valores desejados
                    if conteudo in ["Estudantes internos de ensino a distância", "Estudantes internos de graduação", "Estudantes internos de pós-graduação"]:
                        possui_conteudo = True
                        
                if possui_conteudo==True:
    
                    titulo = soup.find('h1').text

                    dados_servicos.append((titulo, url_servico, datetime.now()))
        

        #tenta se conectar ao banco de dados SQLite
        conn = sqlite3.connect(db_file)

        #cria um objeto cursor, que permite executar comandos SQL no banco de dados
        cursor = conn.cursor()
        #cria a tabela 
        cursor.execute('CREATE TABLE servicos (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, url_servico TEXT, data_insercao DATETIME)')
        #insere os novos dados na tabela "servicos"
        cursor.executemany('INSERT INTO servicos (titulo, url_servico, data_insercao) VALUES (?, ?, ?)', dados_servicos)
        #commita as mudanças no banco de dados
        conn.commit()
        #fecha a conexão com o banco de dados
        conn.close()

else:
    print("Falha ao obter o conteúdo da página:", response.status_code)
