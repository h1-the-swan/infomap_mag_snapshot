#!/bin/bash
#PBS -N extract_subgraph_and_infomap_parallelsql

#PBS -l nodes=1:ppn=16,mem=100gb,feature=16core
#PBS -l walltime=02:30:00

## stderr and stdout go here
#PBS -o /gscratch/stf/jporteno/code/infomap_mag_snapshot/logs/
## Put both the stderr and stdout into a single file
#PBS -j oe

## Sepcify the working directory for this job bundle
#PBS -d /gscratch/stf/jporteno/code/infomap_mag_snapshot/

module load anaconda3_4.2
module load parallel_sql
source activate infomap_mag_snapshot
parallel-sql --sql -a parallel --exit-on-term
source deactivate

