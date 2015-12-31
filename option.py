from optparse import OptionParser
from logger import logger

def args_parse():

    p = OptionParser()
    p.add_option('-e', '--expr', dest='expr', action='append',
                 help='specify experssion')
    p.add_option('-v', '--verbose', dest='verbose', default=20,
                 help='specify verbose level')

    (opts, args) = p.parse_args()

    logger.setLevel(opts.verbose)

    return (opts, args)
