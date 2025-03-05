import logging

def test_logger() -> None:
    logging.debug('this is an debug log')
    logging.info('this is an info log')
    logging.warning('this is an warning log')
    logging.error('this is an error log')
    
    try:
        n = 1 / 0
    except Exception as e:
        logging.exception(f"Exception: {e}")
    
    logging.critical('this is an critical log')
