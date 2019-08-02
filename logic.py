import helpers.rmq_helper as q_helper
import configs.config as conf
import helpers.tlg_helper as tlg
import helpers.database_helper as db


# TODO: log it!
bot = tlg.BotHelper(conf.TOKEN)
cur, database = db.connect(conf.DATABASE)

def on_message(ch, method, properties, body):
    print(" [x] Received %r" % body)
    msg = tlg.Messaging(conf.TOKEN, body, cur = cur, database = database)
    db.add_user(cur, msg.get_user_id(), msg._chat_id, msg.get_name())
    if msg.get_command() is not None:
        msg.command_execute(msg.get_command())
        db.store_message(cur, msg.get_user_id(), msg.get_name(), msg.get_text())
        return 0
    result = bot.sendMessage(msg._chat_id, msg.get_text())
    db.store_message(cur, msg.get_user_id(), msg.get_name(), msg.get_text())
    database.commit()
    return result


if __name__ == '__main__':
    queue_handler = q_helper.QueueHelper(conf.QUEUE_NAME)
    queue_handler.consume_message(on_message)
    queue_handler._channel.start_consuming()
