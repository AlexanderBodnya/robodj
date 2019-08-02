import logging

def exception(logger):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    @param logger: The logging object
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                logger.info('Calling function {}'.format(func.__name__))
                return func(*args, **kwargs)
            except Exception as e:
                # log the exception
                logger.error(e)
                err = "There was an exception in  "
                err += func.__name__
                logger.exception(err)

        return wrapper
    return decorator


def create_logger():
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger('robodj')
    logger.setLevel(logging.DEBUG)
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh = logging.StreamHandler()
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # add handler to logger object
    return logger


def add_logger(logger_name):
    logger = logging.getLogger('robodj.{}'.format(logger_name))
    return logger


logger = create_logger()
