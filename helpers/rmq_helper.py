import pika


# import helpers.log_helper

# TODO: log it!
# function to quick queue set up


class QueueHelper:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self._conn = None
        self._channel = None

    # set connection and return channel

    def connect(self):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            self._channel = self._conn.channel()
            self._channel.queue_declare(queue=self.queue_name, durable=True)

    def _push_message(self, message):
        print('Pushing message to queue', self.queue_name)
        self._channel.basic_publish(exchange='',
                                    routing_key=self.queue_name,
                                    body=message,
                                    # make message persistent
                                    properties=pika.BasicProperties(delivery_mode=2, )
                                    )

    def _consume_message(self, callback):
        self._channel.basic_consume(callback,
                                    queue=self.queue_name,
                                    no_ack=True)

    def push_message(self, message):
        try:
            self._push_message(message)
        except pika.exceptions.ConnectionClosed:
            self.connect()
            self._push_message(message)
        except AttributeError:
            self.connect()
            self._push_message(message)

    def consume_message(self, callback):
        try:
            self._consume_message(callback)
        except pika.exceptions.ConnectionClosed:
            self.connect()
            self._consume_message(callback)
        except AttributeError:
            self.connect()
            self._consume_message(callback)

    def close(self):
        if self._conn and self._conn.is_open:
            self._conn.close()
