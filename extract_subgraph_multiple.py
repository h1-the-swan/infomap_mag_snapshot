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

from h1theswan_utils.network_data import PajekFactory

DEFAULTS = {
    'VERTICES_LABEL': 'Vertices',
    'EDGES_LABEL': 'Arcs'
}

def extract_subgraph_from_edgelist_multiple(fname, names_multiple, sep='\t', header=True, temp_dir=None):
    """TODO: Docstring for parse_edgelist.

    :returns: list of PajekFactory objects corresponding to each of the subsets in `names_multiple`

    """
    # pjk = PajekFactory(temp_dir=temp_dir)
    # one PajekFactory per subset
    # except this opens too many temporary files
    # pjk_multiple = []
    # for nameset_idx in range(len(names_multiple)):
    #     pjk_multiple.append(PajekFactory(temp_dir=temp_dir))
    edges_multiple = []
    for nameset_idx in range(len(names_multiple)):
        # each list will be the edgelist for that subgraph
        edges_multiple.append([])
    rownum = 0
    edges_added = 0
    with open(fname, 'r') as f:
        for i, line in enumerate(f):
            if header is True and i == 0:
                continue
            split = line.strip().split(sep)
            for nameset_idx, nameset in enumerate(names_multiple):
                if ( split[0] in nameset ) and ( split[1] in nameset ):
                    # pjk.add_edge(split[0], split[1])
                    # pjk_multiple[nameset_idx].add_edge(split[0], split[1])
                    edges_multiple[nameset_idx].append( (split[0], split[1]) )
                    edges_added += 1
            rownum += 1
            if (rownum in [1,5,10,50,100,1000,10000,100000,1e6,10e6] or (rownum % 50e6 == 0)):
                logger.debug('rownum: {}. {} edges added'.format(rownum, edges_added))
    # return pjk_multiple
    return edges_multiple


def read_names_file(fname):
    names = []
    with open(fname, 'r') as f:
        for line in f:
            line = line.strip()
            names.append(line)
    return frozenset(names)

def get_names(names_dir):
    fnames = glob(os.path.join(names_dir, '*.txt'))
    fnames.sort()
    names_multiple = []
    for fname in fnames:
        names_multiple.append(read_names_file(fname))
    return names_multiple, fnames

def get_output_fnames(input_fnames, outdir):
    output_fnames = []
    for input_fname in input_fnames:
        output_fname = os.path.basename(input_fname)
        output_fname = os.path.splitext(output_fname)[0]
        output_fname = output_fname + '.net'
        output_fname = os.path.join(outdir, output_fname)
        output_fnames.append(output_fname)
    return output_fnames

def main(args):
    edgelist_fname = os.path.abspath(args.edgelist)

    outdir = os.path.abspath(args.outdir)
    if not os.path.isdir(outdir):
        logger.error("outdir specified does not exist!")
        raise OSError(os.errno.ENOTDIR, os.strerror(os.errno.ENOTDIR), outdir)

    
    start = timer()
    # names_fname = os.path.abspath(args.names)
    # subset_names = read_names_file(names_fname)
    names_dir = os.path.abspath(args.namesdir)
    logger.debug("reading nodes which will identify the subgraph from files in: {}...".format(names_dir))
    if not os.path.isdir(names_dir):
        raise OSError(os.errno.ENOTDIR, os.strerror(os.errno.ENOTDIR), names_dir)
    names_multiple, subset_fnames = get_names(names_dir)
    logger.debug("done reading subset nodes from {}. {} subsets found. ({})".format(names_dir, len(names_multiple), format_timespan(timer()-start)))

    # outfname = os.path.abspath(args.output)
    out_fnames = get_output_fnames(subset_fnames, outdir)
    start = timer()
    logger.debug("getting subgraphs from {} and writing to directory {}...".format(edgelist_fname, outdir))
    header = not args.no_header
    edges_multiple = extract_subgraph_from_edgelist_multiple(edgelist_fname, names_multiple, sep=args.sep, header=header, temp_dir=args.temp_dir)
    logger.debug("extracted subgraphs in {}".format(format_timespan(timer()-start)))

    start = timer()
    num_files_written = 0
    # for i, pjk in enumerate(pjk_list):
    #     with open(out_fnames[i], 'w') as outf:
    #         pjk.write(outf, vertices_label=args.vertices_label, edges_label=args.edges_label)
    #         num_files_written += 1
    for i, edgelist in enumerate(edges_multiple):
        pjk = PajekFactory(temp_dir=args.temp_dir)
        for source, target in edgelist:
            pjk.add_edge(source, target)
        with open(out_fnames[i], 'w') as outf:
            pjk.write(outf, vertices_label=args.vertices_label, edges_label=args.edges_label)
            num_files_written += 1
    logger.debug("done writing {} files to {}. {}".format(num_files_written, outdir, format_timespan(timer()-start)))

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="given the original edgelist file and a directory of text files each with a list of nodes, write the pajek file for the subgraph")
    parser.add_argument("edgelist", help="filename for the original edgelist")
    parser.add_argument("namesdir", help="directory with text files: each a (newline separated) list of node names identifying the subgraph")
    parser.add_argument("outdir", help="directory for the  output pajek files")
    parser.add_argument("--sep", default='\t', help="row delimiter for the input file (default: tab)")
    parser.add_argument("--vertices-label", default=DEFAULTS['VERTICES_LABEL'], help="label for the vertices section (default: {})".format(DEFAULTS['VERTICES_LABEL']))
    parser.add_argument("--edges-label", default=DEFAULTS['EDGES_LABEL'], help="label for the edges section (note:directed graphs should use 'Arcs', undirected graphs should use 'Edges') (default: {})".format(DEFAULTS['EDGES_LABEL']))
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

