import logging


log_level = logging.DEBUG


def create_logger():
    ## Create a custom logger
    custom_logger = logging.getLogger("automatic_dependency_manager")
    custom_logger.setLevel(log_level)
    formatter = logging.Formatter( fmt = "[%(asctime)s] [%(levelname)s]\t[%(filename)s %(funcName)s:%(lineno)s] ['%(msg)s]")
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('ADM.log')
    c_handler.setFormatter(formatter)
    custom_logger.addHandler(c_handler)
    custom_logger.addHandler(f_handler)
    return custom_logger

#
logger = create_logger()

Format = [<asctime>] [<levelname>]\t[<filename> <funcName>:<lineno>] ['<msg>']