from optparse import OptionParser
from logger import logger, FORMAT, get_level
import logging
from os import path, makedirs, rename
import re

def is_dot_included(s):
    reg = re.compile("\\.")
    return re.search(reg, s)

def add_suite(option, opt, value, parser, *args, **kwargs):
    parser.values.suite = value
    for t in parser.rargs:
        if t[0] == '-':
            break;
        else:
            add_test(option, opt, t, parser, *args, **kwargs)

def add_test(option, opt, value, parser, *args, **kwargs):
    if not parser.values.test:
        parser.values.test = []
    if parser.values.suite and not is_dot_included(value):
        parser.values.test.append(parser.values.suite+'.'+value)
    else:
        parser.values.test.append(value)

def args_parse():

    p = OptionParser()
    p.add_option('-e', '--expr', dest='expr', action='append', type='string',
                 help='specify experssion')
    p.add_option('-v', '--verbose', dest='verbose', default='2',
                 help='specify verbose level')
    p.add_option('-o', '--out_dir', dest='out_dir', default='logs', type='string',
                 help='specify output directory')
    p.add_option('-l', '--logfile', dest='logfile', default='dvpy_master.log', type='string',
                 help='specify log filename')
    p.add_option('-m', '--max_agents', dest='max_agents', default=1, type='int',
                 help='specify max agent number')
    p.add_option('-s', '--suite', dest='suite', action='callback', type='string', callback=add_suite,
                 help='specify suite')
    p.add_option('-t', '--test', action='callback', dest='test', type='string', callback=add_test,
                 help='specify test')
    p.add_option('-w', '--where', action='store', dest='where', type='string',
                 help='specify test selector')
    p.add_option('-a', '--action', action='append', dest='action', type='string',
                 help='specify action')
    p.add_option('-f', '--patchfile', action='append', dest='patchfile', type='string',
                 help='specify patch file')

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
