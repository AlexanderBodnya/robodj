import flask
import json
import helpers.tlg_helper as tlg
import configs.config as conf
from helpers.log_helper import add_logger, exception

logger = add_logger(__name__)

app = flask.Flask(__name__)
bot = tlg.BotHelper(conf.TOKEN)

@app.route('/soul_queue', methods=['POST'])
def on_message():

    body = flask.request.get_json()
    print(" [x] Received %r" % body)
    msg = tlg.Messaging(conf.TOKEN, body, conf.DATABASE)
    msg.command_execute()
    msg.resend(conf.TO_CHAT_ID)
    return ('OK', 200)


if __name__ == '__main__':
    bot.deleteWebhook()
    result = bot.setWebhook('https://' + conf.URL + ':' + str(conf.PORT) + '/soul_queue', conf.CERT)
    print(result)
    print(bot.getWebhookInfo())
    print(bot.getMe())
    app.run(host='0.0.0.0', debug=False, port=conf.PORT, ssl_context=(conf.CERT, conf.KEY))
