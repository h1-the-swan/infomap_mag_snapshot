import sys, os, time
from glob import glob
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

# SUBSET_LABEL = '60000-69999'
MISSING_INDICES_FNAME = '/gscratch/stf/jporteno/code/infomap_mag_snapshot/missing_indices_20171228.txt'
# SUBSET_DIRNAME = os.path.join('/gscratch/stf/jporteno/mag_20171110/cluster_nodelists', SUBSET_LABEL)
EDGELIST_FNAME = '/gscratch/stf/jporteno/mag_20171110/PaperReferences_academicgraphdls_20171110.txt'
REPO_DIRNAME = '/gscratch/stf/jporteno/code/infomap_mag_snapshot/'
# LOG_DIR = os.path.join(REPO_DIRNAME, 'logs', 'logs_{}'.format(SUBSET_LABEL))
LOG_DIR = os.path.join(REPO_DIRNAME, 'logs', 'logs_missing'.format(SUBSET_LABEL))

def get_basename(fname):
    b = os.path.basename(fname)
    b = os.path.splitext(b)[0]
    return b

def output_line_for_one_input_file(input_fname):
    # input_fname = os.path.abspath(input_fname)
    b = get_basename(input_fname)
    pjk_fname = "{}.net".format(b)
    pjk_fname = os.path.join(REPO_DIRNAME, 'data', pjk_fname)
    # skip if exists
    if os.path.exists(pjk_fname):
        return None
    log_fname = "{}.log".format(b)
    log_fname = os.path.join(LOG_DIR, log_fname)

    # build the command as a list of strings, which can be concatenated at the end
    out = ['python']
    out.append(os.path.join(REPO_DIRNAME, 'extract_subgraph_and_run_infomap_wrapper.py'))
    out.append(EDGELIST_FNAME)
    out.append(input_fname)
    out.append(pjk_fname)
    out.append('--log-dir {}'.format(LOG_DIR))
    out.append('--no-header')
    out.append('--debug')
    out.append('>& {}'.format(log_fname))  # output stdout and stderr to a file
    out = ' '.join(out)
    return out

# def get_input_filenames(dirname):
#     fnames = glob(os.path.join(dirname, '*.txt'))
#     fnames.sort()
#     fnames = [os.path.abspath(x) for x in fnames]
#     return fnames

def get_missing_input_filenames(missing_indices_fname):
    missing_indices = []
    with open(missing_indices_fname, 'r') as f:
        for line in f:
            line = line.strip()
            this_idx = int(line)
            this_idx = "{:05d}".format(this_idx)
            missing_indices.append(this_idx)



def main(args):
    input_filenames = get_missing_input_filenames(MISSING_INDICES_FNAME)
    outf_number = 0
    while True:
        outfname = 'extract_and_infomap_tasklist_{:03d}.txt'.format(outf_number)
        outfname = os.path.join(REPO_DIRNAME, outfname)
        if not os.path.exists(outfname):
            break
        outf_number += 1

    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)

    # # only do a certain number for now
    # stop_after = 2
    logger.info("writing to {}".format(outfname))
    with open(outfname, 'w') as outf:
        number_written = 0
        for fname in input_filenames:
            b = get_basename(fname)
            file_idx = int(b[:b.find('_')])
            if args.start > 0:
                if file_idx < args.start:
                    continue
            line = output_line_for_one_input_file(fname)
            if line:
                outf.write(line)
                outf.write('\n')
                number_written += 1
            # if number_written == stop_after:
            #     break


if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="write tasklist for use with parallel-sql from a list of missing indices")
    parser.add_argument("--start", type=int, default=0, help="start index")
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
