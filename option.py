from optparse import OptionParser

def args_parse():

    p = OptionParser()
    p.add_option('-e', '--expr', dest='expr', action='append',
                 help='specify experssion')
    #p.add_option('-h', '--help', dest='help', default=False,
    #             help='print help information')

    return p.parse_args()
