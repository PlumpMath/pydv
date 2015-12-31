from optparse import OptionParser
from logger import logger, FORMAT
import logging
from os import path, makedirs

def args_parse():

    p = OptionParser()
    p.add_option('-e', '--expr', dest='expr', action='append',
                 help='specify experssion')
    p.add_option('-v', '--verbose', dest='verbose', default='2',
                 help='specify verbose level')
    p.add_option('-o', '--output', dest='output', default='logs',
                 help='specify output directory')
    p.add_option('-l', '--logfile', dest='logfile', default='dvpy_master.log',
                 help='specify log filename')

    (opts, args) = p.parse_args()

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

    logger.setLevel(get_level(opts.verbose))

    master_log = path.join(opts.output, opts.logfile)
    try:
        makedirs(path.dirname(master_log))
    except Exception as e:
        pass
    fh = logging.FileHandler(master_log)
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(get_level(opts.verbose))

    logger.addHandler(fh)

    return (opts, args)
