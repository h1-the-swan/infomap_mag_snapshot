import sys, os, time, pickle
from datetime import datetime
from timeit import default_timer as timer
from collections import defaultdict
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
        outfname = "{}_dict.pickle".format(outfname)

    header = False
    sep = "\t"

    logger.debug("reading input file: {}...".format(fname))
    start = timer()
    data = defaultdict(set)
    rownum = 0
    with open(fname, 'r') as f:
        for i, line in enumerate(f):
            if header is True and i == 0:
                continue
            line = line.strip().split(sep)
            data[line[0]].add(line[1])
            rownum += 1
            if (rownum in [1,5,10,50,100,1000,10000,100000,1e6,10e6] or (rownum % 50e6 == 0)):
                logger.debug('rownum: {}'.format(rownum))
    logger.debug("done reading data. {}".format(format_timespan(timer()-start)))

    logger.debug("writing to file: {}...".format(outfname))
    start = timer()
    with open(outfname, 'wb') as outf:
        pickle.dump(data, outf)
    logger.debug("done. took {}".format(format_timespan(timer()-start)))

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="take a linklist (edgelist) and get a pickle of a dictionary of citing -> cited")
    parser.add_argument("input", help="input treefile (.tree)")
    parser.add_argument("-o", "--output", help="output filename")
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
