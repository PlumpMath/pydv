from optparse import OptionParser
from logger import logger, FORMAT, get_level
import logging
from os import path, makedirs, rename

def args_parse():

    p = OptionParser()
    p.add_option('-e', '--expr', dest='expr', action='append',
                 help='specify experssion')
    p.add_option('-v', '--verbose', dest='verbose', default='2',
                 help='specify verbose level')
    p.add_option('-o', '--out_dir', dest='out_dir', default='logs',
                 help='specify output directory')
    p.add_option('-l', '--logfile', dest='logfile', default='dvpy_master.log',
                 help='specify log filename')
    p.add_option('-m', '--max_agents', dest='max_agents', default='1',
                 help='specify max agent number')
    p.add_option('-t', '--test', dest='test', action='append',
                 help='specify test')

    (opts, args) = p.parse_args()

    logger.setLevel(get_level(opts.verbose))

    master_log = path.abspath(path.join(opts.out_dir, opts.logfile))
    try:
        makedirs(path.dirname(master_log))
    except Exception as e:
        pass
    if path.exists(master_log):
        rename(master_log, (master_log+'.bak'))
    fh = logging.FileHandler(master_log)
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(get_level(opts.verbose))

    logger.addHandler(fh)

    return (opts, args)
