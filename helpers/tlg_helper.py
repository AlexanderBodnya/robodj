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
        self._chat_id = self.message['message']['chat']['id']
        self.db_url = database_url
        

    @exception(logger)
    def database_connect(self):
        return SQLOperations(self.db_url)


    @exception(logger)
    def command_execute(self):
        commands = {
            '/start': self.start_message,
            '/upvote': self.upvote,
            '/downvote': self.downvote,
            '/suggest': self.suggest,
            '/get_list': self.get_list,
          }
        command, *args = self.get_command()
        if command:
            result = commands[command](*args)
        return result

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
                    return text[entity['offset']:entity['length']], text[entity['length']:].split()
        except KeyError:
            return None, None

    

    @exception(logger)
    def start_message(self, *args, **kwargs):
        self.sendMessage(self._chat_id, 'welcome message')

    @exception(logger)
    def upvote(self, *args, **kwargs):
        self.sendMessage(self._chat_id, 'Not implemented [upvote] method')

    @exception(logger)
    def downvote(self, *args, **kwargs):
        self.sendMessage(self._chat_id, 'Not implemented [downvote] method')


    @exception(logger)
    def suggest(self, *args, **kwargs):
        # db = self.database_connect()
        for arg in args:
            self.sendMessage(self._chat_id, arg)

    @exception(logger)
    def get_list(self, *args, **kwargs):
        self.sendMessage(self._chat_id, 'Not implemented [get_list] method')

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