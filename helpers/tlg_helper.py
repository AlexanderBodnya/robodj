import requests
import json
import helpers.database_helper
from hashlib import md5
from helpers.log_helper import add_logger, exception
from helpers.database_helper import SQLOperations


logger = add_logger(__name__)

class BotHelper:
    # Here we are initializang instance of our bot. It does nothing except stores bot token
    def __init__(self, token):
        self.token = token

    # This is serialized api request. It is separated from api methods because DNRY(do not repeat yourself)
    @exception(logger)
    def api_request(self, method_name, payload={}):
        url = 'https://api.telegram.org/bot' + self.token + '/' + method_name
        # Here we are separating setWebhook method from other methods.
        # setWebhook requires multipart/form-data,
        # requests lib requires to use special parameter files to use the format
        if method_name == 'setWebhook':
            req = requests.post(url, files=payload)
        else:
            req = requests.post(url, data=payload)
        # Here we are trying to handle possible exceptions. It needs to be redesigned, however it works at the moment
        try:
            resp = req.json()
            return 0, resp
        except ValueError:
            return 10
        else:
            return 1

    # This is API method to set webhook. It doesn't have required options, however if you want it to work
    # you need to specify url(this is url on which Telegram will send messages), and path to cert file,
    # in case you are using self-signed certificate
    @exception(logger)
    def setWebhook(self, url=None, cert=None, max_connections=None, allowed_updates=None, **kwargs):
        payload = {
            'url': (None, url)
        }
        # We are checking if parameters are passed and adding them to request
        if cert is not None:
            payload['certificate'] = (cert, open(cert, 'rb'))
        if max_connections is not None:
            payload['max_connections'] = (None, max_connections)
        if allowed_updates is not None:
            payload['allowed_updates'] = (None, allowed_updates)
        payload.update(kwargs)

        result = self.api_request('setWebhook', payload)
        return result

    # This is API method which deletes webhook. It doesn't require any parameters.
    @exception(logger)
    def deleteWebhook(self):
        result = self.api_request('deleteWebhook')
        return result

    # This is API method which returns information about bot. It doesn't require any parameters
    @exception(logger)
    def getMe(self):
        result = self.api_request('getMe')
        return result

    # This is API method which returns information about webhook. It doesn't require any parameters
    @exception(logger)
    def getWebhookInfo(self):
        result = self.api_request('getWebhookInfo')
        return result

    # This is API method to send messages. It requires chat_id and text of the message
    @exception(logger)
    def sendMessage(self, chat_id, text):
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        result = self.api_request('sendMessage', payload)
        return result


class Messaging(BotHelper):

    def __init__(self, token, message, database_url):
        super(Messaging, self).__init__(token)
        self.message = message
        try:
            self._chat_id = self.message['message']['chat']['id']
        except KeyError:
            self._chat_id = self.message['edited_message']['chat']['id']
        self.db =  SQLOperations(database_url)
        



    @exception(logger)
    def command_execute(self):
        commands = {
            '/start': self.start_message,
            '/upvote': self.upvote,
            '/recant_vote': self.recant_vote,
            '/suggest': self.suggest,
            '/get_list': self.get_list,
          }
        command, args = self.get_command()
        if command:
            result = commands[command](args)
            return result
        else:
            return None

    @exception(logger)
    def get_name(self, *args, **kwargs):
        name = self.message['message']['from']['username']
        return name

    @exception(logger)
    def get_user_id(self, *args, **kwargs):
        _id = self.message['message']['from']['id']
        return _id

    @exception(logger)
    def get_text(self, *args, **kwargs):
        text = self.message['message']['text']
        return text

    @exception(logger)
    def get_command(self):
        text = self.get_text()
        try:
            entities = self.message['message']['entities']
            for entity in entities:
                if entity['type'] == 'bot_command':
                    command = text[entity['offset']:entity['length']]
                    args_list = text[entity['length']:].split()
                    return command, args_list
        except KeyError:
            return None, None

    

    @exception(logger)
    def start_message(self, *args, **kwargs):
        self.sendMessage(self._chat_id, 'Вас привествует бот для предложения песен на афтерпати! Для того чтобы узнать какие песни уже успели предложить воспользуйтесь командой:\n\t/get_list\nДля того чтобы предложить свою песню воспользуйтесь командой:\n\t/suggest Название Песни\nДля того чтобы проголосовать за песню из списка воспользуйтесь командой:\n\t/upvote <порядковый номер песни>\nДля того чтобы отозвать свой голос воспользуйтесь командой:\n\t/recant_vote <порядковый номер песни>\nЕсли за песню не будет одного голоса она автоматически пропадет из списка!')

    @exception(logger)
    def upvote(self, *args, **kwargs):
        try:
            song_id = int(args[0][0])
            resp = self.db.get_song_name_by_id(song_id)
            logger.info('Song name is {}'.format(resp))
            voter_id = self.get_user_id()
            song_name = resp[0]
            vote_pk = self.vote_hash(song_name, voter_id)
            self.db.add_data('VoteLog', vote_id=vote_pk, song_name=song_name, voter_id=voter_id)
            self.db.destroy_session()
            self.sendMessage(self._chat_id, '{} проголосовал(а) за песню {}!'.format(self.get_name(), song_name))
        except:
            self.sendMessage(self._chat_id, 'Пожалуйста укажите существующий порядковый номер песни!')
        

    @exception(logger)
    def recant_vote(self, *args, **kwargs):
        try:
            song_id = int(args[0][0])
            resp = self.db.get_song_name_by_id(song_id)
            logger.info('Song name is {}'.format(resp))
            voter_id = self.get_user_id()
            song_name = resp[0]
            vote_pk = self.vote_hash(song_name, voter_id)
            self.db.recant_vote(vote_pk)
            self.db.destroy_session()
            self.sendMessage(self._chat_id, '{} отозвал(а) свой голос за песню {}!'.format(self.get_name(), song_name))
        except:
            self.sendMessage(self._chat_id, 'Пожалуйста укажите существующий порядковый номер песни!')


    @exception(logger)
    def suggest(self, *args, **kwargs):
        try:
            logger.info('Args are {}'.format(args[0]))
            if args[0]:
                song_name = ' '.join(args[0])
                voter_id = self.get_user_id()
                vote_pk = self.vote_hash(song_name, voter_id)
                self.db.add_data('VoteLog', vote_id=vote_pk, song_name=song_name, voter_id=voter_id)
                self.db.add_data('SongsList', song_name=song_name)
                self.db.destroy_session()
                self.sendMessage(self._chat_id, '{} добавил(а) в голосование песню {}!'.format(self.get_name(), song_name))
            else:
                self.sendMessage(self._chat_id, 'Укажите название песни!')
        except:
            self.sendMessage(self._chat_id, 'Укажите название песни!')

    @exception(logger)
    def get_list(self, *args, **kwargs):
        text = 'Список песен в голосовании:\n'
        resp = self.db.get_list()
        self.db.destroy_session()
        if resp:
            for item in resp:
                line = '№ {} - {} - Количество голосов: {} \n'.format(str(item[0]), str(item[1]), str(item[2]))
                text += line
        else:
            text = 'Список голосования пуст!'
        self.sendMessage(self._chat_id, text)

    @exception(logger)
    def vote_hash(self, *args):
        string = ''
        for arg in args:
            logger.debug('Arg is {}'.format(arg))
            string += str(arg)

        hashed = md5(string.encode('utf-8')).hexdigest()
        logger.debug('String to hash - {}'.format(string))
        logger.debug('Resulting hash - {}'.format(hashed))
        return hashed