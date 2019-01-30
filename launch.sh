#!/bin/bash

# Jody Pacalon, Jan 2019

# Script for launching multiple model productions using JOB_INIT.sh and masterscript.py 
# in Cicada.
# You need :
#	1. an input_rec.txt with one rec by line.
#	2. a template_files folder containing alignment.pir, JOB_INIT.sh, ref_model.pdb,
#	   templates folder with templates .pdb, models/ a_models/ and p_models/ empty folders.


while read i; do
	cp -r template_files/ $i/
	cd $i/
	sed "s/NAME/$i/g" JOB_INIT.sh > job.sh
	chmod +x job.sh 
	oarsub -S ./job.sh
	cd ..
done <input_rec.txt
