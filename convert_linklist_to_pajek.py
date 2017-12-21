import sys, os, time
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger('__main__').getChild(__name__)

from babel_util.util.PajekFactory import PajekFactory

DEFAULTS = {
    'VERTICES_LABEL': 'Vertices',
    'EDGES_LABEL': 'Arcs'
}

def parse_edgelist(fname, sep='\t', header=True, temp_dir=None):
    """TODO: Docstring for parse_edgelist.

    :fname: TODO
    :sep: TODO
    :returns: PajekFactory object

    """
    pjk = PajekFactory(temp_dir=temp_dir)
    rownum = 0
    with open(fname, 'r') as f:
        for i, line in enumerate(f):
            if header is True and i == 0:
                continue
            split = line.strip().split(sep)
            pjk.add_edge(split[0], split[1])
            rownum += 1
            if (rownum in [1,5,10,50,100,1000,10000,100000,1e6,10e6] or (rownum % 50e6 == 0)):
                logger.debug('{} edges added'.format(rownum))
    return pjk

    #
    # logger.info('writing to file {}'.format(args.outfile))
    # with open(args.outfile, 'w') as outf:
    #     pjk.write(outf)
def main(args):
    fname = os.path.abspath(args.input)
    logger.debug("using input file: {}".format(fname))
    if args.output:
        outfname = os.path.abspath(args.output)
    else:
        outfname = os.path.basename(fname)
        outfname = os.path.splitext(outfname)[0]
        outfname = "{}.net".format(outfname)
        outfname = os.path.abspath(outfname)
    logger.debug("will write to output file: {}".format(outfname))

    start = timer()
    logger.debug("parsing the edgelist...")
    header = not args.no_header
    pjk = parse_edgelist(fname, header=header, temp_dir=args.temp_dir)
    logger.debug("done reading edgelist. {}".format(timer()-start))

    start = timer()
    logger.debug("writing to file...")
    with open(outfname, 'w') as outf:
        pjk.write(outf, vertices_label=args.vertices_label, edges_label=args.edges_label)
    logger.debug("done writing to file. {}".format(timer()-start))


if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="convert linklist (edge list) to pajek")
    parser.add_argument("input", help="input filename")
    parser.add_argument("-o", "--output", help="output filename (default: use input basename)")
    parser.add_argument("--sep", default='\t', help="row delimiter for the input file (default: tab)")
    parser.add_argument("--vertices-label", default=DEFAULTS['VERTICES_LABEL'], help="label for the vertices section (default: {})".format(DEFAULTS['VERTICES_LABEL']))
    parser.add_argument("--edges-label", default=DEFAULTS['EDGES_LABEL'], help="label for the edges section (note:directed graphs should use 'Arcs', undirected graphs should use 'Edges') (default: {})".format(DEFAULTS['VERTICES_LABEL']))
    parser.add_argument("--temp-dir", help="directory to store temporary files", default=None)
    parser.add_argument("--no-header", action='store_true', help="specifies that there is no header row in the input file")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    else:
        logger.setLevel(logging.INFO)
    if args.sep.lower() == 'tab':
        args.sep = '\t'
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
