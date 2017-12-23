#!/bin/bash
#PBS -N extract_subgraph_and_infomap_test

#PBS -l nodes=1:ppn=16,mem=100gb,feature=16core
#PBS -l walltime=01:00:00

## stderr and stdout go here
#PBS -o /gscratch/stf/jporteno/code/infomap_mag_snapshot/logs/
## Put both the stderr and stdout into a single file
#PBS -j oe

## Sepcify the working directory for this job bundle
#PBS -d /gscratch/stf/jporteno/code/infomap_mag_snapshot/

module load anaconda3_4.2
source activate infomap_mag_snapshot
python /gscratch/stf/jporteno/code/infomap_mag_snapshot/extract_subgraph_and_run_infomap_wrapper.py /gscratch/stf/jporteno/mag_20171110/PaperReferences_academicgraphdls_20171110.txt /gscratch/stf/jporteno/mag_20171110/cluster_nodelists/00000-09999/09999_PaperReferences_academicgraphdls_20171110_cluster-732204.txt /gscratch/stf/jporteno/code/infomap_mag_snapshot/data/09999_PaperReferences_academicgraphdls_20171110_cluster-732204.net --no-header --debug
source deactivate
