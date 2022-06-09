import logging

FORMAT = '%(asctime)s. %(name)s-%(levelname)s: %(message)s'

def get_logger(name: str = __name__, level: str = "INFO"):
    logging.basicConfig(format=FORMAT, level=getattr(logging, level.upper()))
    return logging.getLogger(name)
