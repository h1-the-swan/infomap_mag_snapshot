import sys, os, time
from datetime import datetime
from timeit import default_timer as timer
from collections import defaultdict
from six import itervalues
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

def main(args):
    fname = os.path.abspath(args.input)
    if args.output:
        outfname = os.path.abspath(args.output)
    else:
        outfname = os.path.splitext(fname)[0]
        outfname = "{}_paperids_in_small_clusters.txt".format(outfname)

    logger.debug("reading input file: {}...".format(fname))
    start = timer()
    data = defaultdict(list)
    with open(fname, 'r') as f:
        for line in f:
            if line[0] == "#":
                # skip comment lines
                continue
            line = line.strip().split(" ")
            cl = line[0]
            toplevel_cl = cl.split(":")[0]
            id = line[2].strip('"')
            data[toplevel_cl].append(id)
    logger.debug("done reading data. {}".format(format_timespan(timer()-start)))

    logger.debug("opening file for write: {}".format(outfname))
    outf = open(outfname, 'w')
    logger.debug("getting ids and writing to file...")
    start = timer()
    num_clusters = 0
    num_ids = 0
    for id_list in itervalues(data):
        if len(id_list) <= args.threshold:
            num_clusters += 1
            for id in id_list:
                num_ids += 1
                outf.write(str(id))
                outf.write("\n")
    outf.close()
    logger.debug("done. took {}".format(format_timespan(timer()-start)))
    logger.debug("got {} ids from {} clusters".format(num_ids, num_clusters))


if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="get a list of all of the paper ids in small top-level clusters (below a certain threshold size)")
    parser.add_argument("input", help="input treefile (.tree)")
    parser.add_argument("-o", "--output", help="output filename")
    parser.add_argument("--threshold", type=int, default=1000, help="get all papers in top-level clusters with size equal to or less than this threshold (default: 1000)")
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
