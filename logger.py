import logging

FORMAT = '[DVPY %(asctime)s] %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger('dvpy')

def get_level(level):
    mapping = {'1' : logging.DEBUG,
               '2' : logging.INFO,
               '3' : logging.WARNING,
               '4' : logging.ERROR,
               '5' : logging.CRITICAL}
    if level in mapping:
        return mapping[level]
    else:
        raise Exception('unsupported verbose level ' + level)
