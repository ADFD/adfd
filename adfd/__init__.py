import logging


def configure_logging(level=logging.DEBUG):
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(filename)s %(funcName)s:%(lineno)d '
               '%(levelname)s: %(message)s')


configure_logging("INFO")
