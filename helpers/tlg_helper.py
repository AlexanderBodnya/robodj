import requests
import json
import helpers.database_helper
from helpers.log_helper import add_logger, exception


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

    def __init__(self, token, message, **kwargs):
        super(Messaging, self).__init__(token)
        self.message = message
        self._json_message = json.loads(message.decode('utf-8'))
        self._chat_id = self._json_message['message']['chat']['id']
        self.cur = kwargs.get('cur', None)
        self.database = kwargs.get('database', None)

    @exception(logger)
    def command_execute(self, command):
        commands = {
            'start': self.start_message,
            'get_chat_id': self.return_chat_id,
            'get_name': self.return_name,
            'get_id': self.return_user_id,
            'get_users': self.get_users
        }
        result = commands[command]()
        return result
    # Deprecated, moved to instance initialization
    # def get_chat_id(self):
    #     chat_id = self._json_message['message']['chat']['id']
    #     return chat_id

    @exception(logger)
    def get_name(self):
        name = self._json_message['message']['from']['username']
        return name

    @exception(logger)
    def get_user_id(self):
        id = self._json_message['message']['from']['id']
        return id

    @exception(logger)
    def get_text(self):
        text = self._json_message['message']['text']
        return text

    @exception(logger)
    def get_command(self):
        words = self.get_text().split()
        if words[0][0] == '/':
            return words[0][1:]
        else:
            return None

    @exception(logger)
    def start_message(self):
        self.sendMessage(self._chat_id, 'welcome message')

    @exception(logger)
    def return_chat_id(self):
        self.sendMessage(self._chat_id, self._chat_id)

    @exception(logger)
    def return_name(self):
        self.sendMessage(self._chat_id, self.get_name())

    @exception(logger)
    def return_user_id(self):
        self.sendMessage(self._chat_id, self.get_user_id())

    @exception(logger)
    def get_users(self):
        self.cur.execute('SELECT * FROM users')
        results = self.cur.fetchall()
        self.sendMessage(self._chat_id, results)
