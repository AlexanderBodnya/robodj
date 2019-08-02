import logging
import logging.handlers
import time


class LogHelper(logging.Logger):
    # Redefining logging levels for convenience purposes
    levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG
    }

    # Instance initialization function takes logger name as argument and provides
    # instance of logger with defined format parameters
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.formatter = logging.Formatter(
            '%(processName)s %(process)d %(levelname)s %(asctime)s %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )

    # Redefined logging.log function, which allows to take logging levels as int numbers
    def log_message(self, level, *args):
        self.logger.log(self.levels[level], *args)

    # Set log level of the logger instance
    def set_level(self, log_level):
        self.logger.setLevel(self.levels[log_level])

    # Create handler to send logs to the file
    def file_handler(self):
        filename = time.strftime("%Y%m%d-%H%M%S") + '_soulbot.log'
        handler = logging.FileHandler(filename)
        handler.setFormatter(self.formatter)
        return handler

    # Create handler to send logs to the stdout
    def stream_handler(self):
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)
        return handler

    # Attach handler tot the logger instance
    def attach_handler(self, handler):
        self.logger.addHandler(handler)

    def log_decorator(self, log_level):
        def decorator_wrapper(func):
            def function_wrapper(*args, **kwargs):
                self.log_message(log_level, 'Starting %s execution', func.__name__)
                res = func(*args, **kwargs)
                self.log_message(log_level, 'Function %s returned %s', func.__name__, res)
                return res

            return function_wrapper

        return decorator_wrapper


# some examples
# log = LogHelper('test_log')
# log.set_level(3)

# sh = log.stream_handler()
# log.attach_handler(sh)
# log.log_message(3, '%s before you %s', 'Look', 'leap!')
# handler = log.file_handler()
# log.attach_handler(handler)


# log.log_message(0, '%s before you %s', 'Look', 'leap!')
# log.log_message(3, '%s before you %s', 'Look', 'leap!')
# log.log_message(4, '%s before you %s', 'Look', 'leap!')


# @log.log_decorator(0)
# def test():
#     print('test')
#     return 1
#
#
# test()
