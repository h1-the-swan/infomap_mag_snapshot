# for running on HPC
# remember to run module load anaconda3_4.2 and then `source activate infomap_mag_snapshot` in the job script

import sys, os, time, subprocess
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

DEFAULTS = {
    'VERTICES_LABEL': 'Vertices',
    'EDGES_LABEL': 'Arcs',
    'PATH_TO_INFOMAP': '/gscratch/stf/jporteno/infomap/Infomap',
    'INFOMAP_OUTDIR': '/gscratch/stf/jporteno/code/infomap_mag_snapshot/data/',
    'LOG_DIR': '/gscratch/stf/jporteno/code/infomap_mag_snapshot/logs'
}

from extract_subgraph import main as extract_subgraph_write_pajek

def get_basename(fname):
    b = os.path.basename(fname)
    b = os.path.splitext(b)[0]
    return b

def main(args):
    extract_subgraph_write_pajek(args)
    pjk_fname = os.path.abspath(args.output)
    output_basename = get_basename(pjk_fname)
    log_fname = os.path.join(DEFAULTS['LOG_DIR'], "{}.log".format(output_basename))
    log_fname = os.path.abspath(log_fname)
    log_f = open(log_fname, 'w')
    cmd = [DEFAULTS['PATH_TO_INFOMAP'], pjk_fname, DEFAULTS['INFOMAP_OUTDIR'], '-t', '-vvv']
    logger.debug("running Infomap on file {}. outputting to directory: {}. logging stdout and stderr to {}".format(cmd[1], cmd[2], log_fname))
    completed_process = subprocess.run(cmd, stdout=log_f, stderr=subprocess.STDOUT)

    log_f.close()
    logger.debug("Infomap process completed with status code: {}".format(completed_process.returncode))

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="extract subgraph and then run infomap")
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
