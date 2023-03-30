import logging


def get_logger(name: str = '_root_'):
    logging.basicConfig(format='%(levelname)s: %(asctime)s - %(name)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.INFO,
                        handlers=[
                            logging.FileHandler("../debug.log"),
                            logging.StreamHandler()
                        ]
                        )

    logger = logging.getLogger(name)
    return logger