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

from h1theswan_utils.network_data import edgelist_to_pajek

DEFAULTS = {
    'VERTICES_LABEL': 'Vertices',
    'EDGES_LABEL': 'Arcs'
}

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
    # pjk = parse_edgelist(fname, header=header, temp_dir=args.temp_dir)
    pjk = edgelist_to_pajek(fname, sep=args.sep, header=header, temp_dir=args.temp_dir, weighted=False)
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
