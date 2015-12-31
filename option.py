from optparse import OptionParser

def args_parse():

    p = OptionParser()
    p.add_option('-e', '--expr', dest='expr', action='append',
                 help='specify experssion')

    (opts, args) = p.parse_args()

    return (opts, args)
