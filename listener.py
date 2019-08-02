import flask
import json
import helpers.tlg_helper as tlg
import configs.config as conf
import helpers.rmq_helper as q_helper
import logging

app = flask.Flask(__name__)
bot = tlg.BotHelper(conf.TOKEN)

global channel
queue = 'bot_inbox'


@app.route('/soul_queue', methods=['POST'])
def on_message():
    print('GOT SOMETHING')
    logging.error('Message is {}'.format(flask.request.get_json()))
    return ('OK', 200)


if __name__ == '__main__':
    bot.deleteWebhook()
    result = bot.setWebhook('https://' + conf.URL + ':' + str(conf.PORT) + '/soul_queue', conf.CERT)
    print(result)
    print(bot.getWebhookInfo())
    print(bot.getMe())
    app.run(host='0.0.0.0', debug=False, port=conf.PORT, ssl_context=(conf.CERT, conf.KEY))
