from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import subprocess
import threading
import sqlite3
import Levenshtein

#função de similaridade usando o algoritmo de Levenshtein
def similarity(s1, s2):
    return Levenshtein.ratio(s1, s2)

#conexão com o banco de dados SQLite
conn = sqlite3.connect('actions/banco_de_dados/banco_de_dados.db')

#registro da função de similaridade no SQLite
conn.create_function('similarity', 2, similarity)

class ActionVerificarBancoDeDados(Action):
    def name(self) -> Text:
        return "action_verificar_banco_de_dados"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #chama o script usando o subprocess
        threading.Thread(target=subprocess.Popen, args=(["python", "actions/script/script.py"],)).start()

        return []


class ActionEncontrarServico(Action):

    def name(self) -> Text:
        return "action_encontrar_servico"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #obtém a penúltima mensagem do usuário
        penultima_mensagem = tracker.get_last_event_for(event_type="user", skip=1)
        #obtém a entidade da penúltima mensagem
        entidade = penultima_mensagem.get("parse_data", {}).get("entities", [])

        if entidade:
            global servico
            #obtém o valor da entidade
            servico = entidade[0]["value"]

            try:
                #consulta o banco de dados para obter os cinco serviços mais parecidos com a mensagem do usuário
                cursor = conn.execute("SELECT titulo, url_servico FROM servicos ORDER BY similarity(titulo, ?) DESC LIMIT 5", (servico,))
                titulos_parecidos = cursor.fetchall()

                #envia os cinco serviços mais parecidos de volta para o usuário, cada um hiperlinkado
                if titulos_parecidos:
                    mensagem = 'Os cinco serviços mais parecidos com "{}" são:'.format(servico)
                    for titulo, url_servico in titulos_parecidos:
                        mensagem += "\n- [{}]({})".format(titulo, url_servico)

                    dispatcher.utter_message(text=mensagem)

                    opcoes_resposta = [{'title': 'Sim', 'payload': '/sim'}, {'title': 'Não', 'payload': '/mais_cinco_servicos'}]
                    mensagem_opcoes = "Era isso que você estava procurando?"
                    dispatcher.utter_message(text=mensagem_opcoes, buttons=opcoes_resposta)

                else:
                    mensagem = "Aguarde um momento, estou atualizando o banco de dados..."
                    dispatcher.utter_message(text=mensagem)

            except:
                mensagem = "Aguarde um momento, estou inserindo os dados no banco de dados..."
                dispatcher.utter_message(text=mensagem)

        else:
            dispatcher.utter_message(text="Não consegui encontrar o serviço.")
            dispatcher.utter_message(text='Me envie uma mensagem assim: "Encontrar: SERVIÇO QUE VOCÊ DESEJA ENCONTRAR".')


        return []

class ActionMaisCincoServicos(Action):

    def name(self) -> Text:
        return "action_mais_cinco_servicos"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #consulta o banco de dados para obter os próximos cinco serviços com títulos mais parecidos
        cursor = conn.execute("SELECT titulo, url_servico FROM servicos ORDER BY similarity(titulo, ?) DESC LIMIT 5 OFFSET 5", (servico,))
        titulos_parecidos = cursor.fetchall()

        if titulos_parecidos:
            #monta a mensagem com os serviços encontrados
            mensagem = 'Os próximos cinco serviços mais parecidos com "{}" são:'.format(servico)
            for titulo, url_servico in titulos_parecidos:
                mensagem += "\n- [{}]({})".format(titulo, url_servico)

            #envia a mensagem ao usuário
            dispatcher.utter_message(text=mensagem)
            
            opcoes_resposta = [{'title': 'Sim', 'payload': '/sim'}, {'title': 'Não', 'payload': '/perguntar'}]
            mensagem_opcoes = "Era isso que você estava procurando?"
            dispatcher.utter_message(text=mensagem_opcoes, buttons=opcoes_resposta)

        else:
            mensagem = "Não há mais serviços disponíveis."
            dispatcher.utter_message(text=mensagem)



        return []


class ActionPesquisarGoogle(Action):

    def name(self) -> Text:
        return "action_pesquisar_google"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #monta o link, substituindo o espaço por "+"
        link = "https://www.google.com/search?q=" + servico.replace(' ', '+') + "+site:portal.ufvjm.edu.br"

        mensagem = "Sinto muito por não conseguir te ajudar. No entanto, posso sugerir que você dê uma olhada neste link específico do Google: [{}]({}).".format(link, link)

        dispatcher.utter_message(text=mensagem)

        return []