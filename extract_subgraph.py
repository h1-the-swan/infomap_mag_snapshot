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

from h1theswan_utils.network_data import extract_subgraph_from_pajek_and_write_to_pajek

def read_names_file(fname):
    names = []
    with open(fname, 'r') as f:
        for line in f:
            line = line.strip()
            names.append(line)
    return names

def main(args):
    pjk_fname = os.path.abspath(args.pajekfile)
    
    start = timer()
    names_fname = os.path.abspath(args.names)
    logger.debug("reading nodes which will identify the subgraph from file: {}...".format(names_fname))
    subset_names = read_names_file(names_fname)
    logger.debug("done reading subset nodes from {}. {} nodes found. ({})".format(names_fname, len(subset_names), format_timespan(timer()-start)))

    outfname = os.path.abspath(args.output)
    start = timer()
    logger.debug("getting subgraph from {} and writing to {}...".format(pjk_fname, outfname))
    extract_subgraph_from_pajek_and_write_to_pajek(pjk_fname, subset_names, outfname)
    logger.debug("done writing to {}. {}".format(outfname, format_timespan(timer()-start)))

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="given the original pajek file and a text file with a list of nodes, write the pajek file for the subgraph")
    parser.add_argument("pajekfile", help="filename for the original pajek network file (.net)")
    parser.add_argument("names", help="text file (newline separated) list of node names identifying the subgraph")
    parser.add_argument("output", help="filename for the output pajek file (.net)")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    else:
        logger.setLevel(logging.INFO)
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
