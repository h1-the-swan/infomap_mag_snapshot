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

from h1theswan_utils.treefiles import Treefile

def output_to_file(counts, outfname, sep='\t'):
    series_name = counts.name
    counts.name = 'num_papers'
    counts.to_csv(outfname, header=True, sep=sep, index_label=series_name)

def main(args):
    fname = os.path.abspath(args.input)
    outfname = args.output
    if not outfname:
        outfname = os.path.basename(fname)
        outfname = os.path.splitext(outfname)[0]
        outfname = outfname + '_topcluster_counts.tsv'
    outfname = os.path.abspath(outfname)

    treefile = Treefile(fname)
    start = timer()
    logger.debug("parsing treefile: {}...".format(fname))
    treefile.parse()
    logger.debug("done parsing treefile {}. {}".format(fname, format_timespan(timer()-start)))
    
    start = timer()
    logger.debug("getting top-level cluster counts for treefile {} (already parsed)".format(fname))
    counts = treefile.top_cluster_counts()
    logger.debug("done getting top-level cluster counts for treefile {}. {}".format(fname, format_timespan(timer()-start)))

    start = timer()
    logger.debug("writing to output file: {}...".format(outfname))
    output_to_file(counts, outfname, sep=args.sep)
    logger.debug("done writing to output file {}. {}".format(outfname, format_timespan(timer()-start)))

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="given a tree file, output a tsv with top-level clusters and counts")
    parser.add_argument("input", help="input treefile (.tree)")
    parser.add_argument("-o", "--output", help="output filename. default: use input basename")
    parser.add_argument("--sep", default="\t", help="delimiter for the output file. default: tab")
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
