import logging


def configure_logging(level=logging.DEBUG):
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(filename)s %(funcName)s:%(lineno)d "
        "%(levelname)s: %(message)s",
    )
    logging.getLogger().log(
        logging.getLevelName(level), f"logging initialized with level {level}"
    )
