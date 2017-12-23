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

from h1theswan_utils.network_data import PajekFactory

DEFAULTS = {
    'VERTICES_LABEL': 'Vertices',
    'EDGES_LABEL': 'Arcs'
}

def extract_subgraph_from_edgelist(fname, names, sep='\t', header=True, temp_dir=None):
    """TODO: Docstring for parse_edgelist.

    :fname: TODO
    :sep: TODO
    :returns: PajekFactory object

    """
    pjk = PajekFactory(temp_dir=temp_dir)
    rownum = 0
    edges_added = 0
    with open(fname, 'r') as f:
        for i, line in enumerate(f):
            if header is True and i == 0:
                continue
            split = line.strip().split(sep)
            if ( split[0] in names ) and ( split[1] in names ):
                pjk.add_edge(split[0], split[1])
                edges_added += 1
            rownum += 1
            if (rownum in [1,5,10,50,100,1000,10000,100000,1e6,10e6] or (rownum % 50e6 == 0)):
                logger.debug('rownum: {}. {} edges added'.format(rownum, edges_added))
    return pjk


def read_names_file(fname):
    names = []
    with open(fname, 'r') as f:
        for line in f:
            line = line.strip()
            names.append(line)
    return frozenset(names)

def main(args):
    edgelist_fname = os.path.abspath(args.edgelist)
    
    start = timer()
    names_fname = os.path.abspath(args.names)
    logger.debug("reading nodes which will identify the subgraph from file: {}...".format(names_fname))
    subset_names = read_names_file(names_fname)
    logger.debug("done reading subset nodes from {}. {} nodes found. ({})".format(names_fname, len(subset_names), format_timespan(timer()-start)))

    outfname = os.path.abspath(args.output)
    start = timer()
    logger.debug("getting subgraph from {} and writing to {}...".format(edgelist_fname, outfname))
    header = not args.no_header
    pjk = extract_subgraph_from_edgelist(edgelist_fname, subset_names, sep=args.sep, header=header, temp_dir=args.temp_dir)
    logger.debug("extracted subgraph in {}".format(format_timespan(timer()-start)))

    start = timer()
    with open(outfname, 'w') as outf:
        pjk.write(outf, vertices_label=args.vertices_label, edges_label=args.edges_label)
    logger.debug("done writing to {}. {}".format(outfname, format_timespan(timer()-start)))

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="given the original pajek file and a text file with a list of nodes, write the pajek file for the subgraph")
    parser.add_argument("edgelist", help="filename for the original edgelist")
    parser.add_argument("names", help="text file (newline separated) list of node names identifying the subgraph")
    parser.add_argument("output", help="filename for the output pajek file (.net)")
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
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
