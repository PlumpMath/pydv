from optparse import OptionParser
from logger import logger, FORMAT
import logging
from os import path, makedirs

def args_parse():

    p = OptionParser()
    p.add_option('-e', '--expr', dest='expr', action='append',
                 help='specify experssion')
    p.add_option('-v', '--verbose', dest='verbose', default=logging.INFO,
                 help='specify verbose level')
    p.add_option('-o', '--output', dest='output', default='logs',
                 help='specify output directory')
    p.add_option('-l', '--logfile', dest='logfile', default='dvpy_master.log',
                 help='specify log filename')

    (opts, args) = p.parse_args()

    logger.setLevel(opts.verbose)

    master_log = path.join(opts.output, opts.logfile)
    try:
        makedirs(path.dirname(master_log))
    except Exception as e:
        pass
    fh = logging.FileHandler(master_log)
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(opts.verbose)

    logger.addHandler(fh)

    return (opts, args)
