#!/usr/bin/env python3
# coding: utf-8 
# Jody PACALON, Oct 2018

''' 
Script for generating models, then align and protonate them.
You need to pass the receptor name in argument to the script,
like > masterpiece_cicada.py -i hOR2J3
Your current folder need to have :
        - templates/  folder (with all the templates files you use).
        - aignment.pir file, for MODELLER.
        - ref_model.pdb file, for CPPTRAJ to align your models.
        - models/ a_models/ and p_models/ folders (create them before lauching).
'''

##################################################################
#                                                 MODULES IMPORT                         #
##################################################################

import time
import os
from modeller import *
from modeller.automodel import *
import glob     # Retrive files/folders
import sys, getopt

##################################################################
#                                                 PARAMETERS                             #
##################################################################

rec_list = []

def main(argv):
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print ('masterpiece_cicada.py -i <rec_list>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('masterpiece_cicada.py -i <rec_list>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         rec_list.append(arg)

if __name__ == "__main__":
   main(sys.argv[1:])


##################################################################
# Principal folder path :
folder_path = os.getcwd()

models_path = folder_path + "/models"
a_models_path = folder_path + "/a_models"
p_models_path = folder_path + "/p_models"

######################### MODELLER PARAM #########################
# List of templates used :
template_list = ("1U19-claire", "2LNL", "2YDV-claire", "3ODU-claire")

# Number of generated models by receptor :
num_gen = 1000

######################### PROPKA PARAM ###########################
# Location of pdb2pqr
#pdb2pqr = "/home/Softwares/pdb2pqr_2.0.0/pdb2pqr"

# pH of protonated models
ph_list = [6.5]


##################################################################
#                                                 MODELLER                               #
##################################################################

start = time.time()

for rec in rec_list:

        log.verbose()
        env = environ()
        env.io.atom_files_directory = [".", "templates/"]
        a = automodel(env,
                alnfile = "alignment.pir",
                knowns = template_list,
                sequence = rec)
        a.starting_model = 1
        a.ending_model = num_gen
        a.library_shedule = autosched.slow
        a.max_var_iterations = 300
        a.md_level = refine.slow
        a.make()
        os.system("mkdir {0}/{1}".format(models_path, rec))
        os.system("rm *{0}.ini *{0}.rsr *{0}.sch *{0}.V9999* *{0}.D0000*".format(rec))
        os.system("mv {0}*.pdb {1}/{0}/".format(rec, models_path))


##################################################################
#                             CPPTRAJ                            #
##################################################################

########################### FUNCTION #############################

def trajin_gen(target):

        '''
        #Create a CPPTRAJ trajin file to align one pdb model into an other (template) pdb model.
        #Needs : 
        #       - Name of the target.
        '''

        with open("align.trajin", "w") as filout:
                filout.write("parm {}\n".format(target))        # Load the target top file
                filout.write("trajin {}\n".format(target))      # Load the pdb file
                filout.write("parm ref_model.pdb\n")
                filout.write("reference ref_model.pdb parm ref_model.pdb [REF]\n")
                filout.write("rms align ref [REF] :6-25,40-62,76-100,118-135,176-197,215-238,250-265&@CA= :6-25,40-62,76-100,118-135,176-197,215-238,250-265&@CA=\n")
                filout.write("trajout a_{0} pdb {0} pdb\n".format(target))
##################################################################

for rec in rec_list:

        # Create all subfolders in a_models
        os.system("mkdir {0}/a_{1}".format(a_models_path, rec))

        # Create list of all non aligned models previously created
        model_list = os.listdir("{0}/{1}/".format(models_path, rec))

        for model in model_list:

                # Generation of trajin file
                trajin_gen(model)

                # Copy of the model in folder path
                os.system("cp {0}/{1}/{2} .".format(models_path, rec, model))

                # Make the alignment with CPPTRAJ
                os.system("/home/jpacalon/soft/amber18/bin/cpptraj -i align.trajin")

                # Clean files
                os.system("rm align.trajin {0} ".format(model))

                # Move aligned model in right folder
                os.system("mv a_{0} {1}/a_{2}/".format(model, a_models_path, rec))


##################################################################
#                                                 PROPKA                                 #
##################################################################

for rec in rec_list:

        # Create all subfolders in p_models
        os.system("mkdir {0}/p_{1}".format(p_models_path, rec))

        # Create list of all aligned models previously created
        aligned_model_list = os.listdir("{0}/a_{1}/".format(a_models_path, rec))

        for model in aligned_model_list:

                # Copy of the model in folder path
                os.system("cp {0}/a_{1}/{2} .".format(a_models_path, rec, model))

                # Protonate the model using propka
                for ph in ph_list:
                        os.system("/home/jpacalon/soft/apbs-pdb2pqr-master/pdb2pqr/pdb2pqr.py --ff=amber --ffout=amber --ph-calc-method=propka --with-ph={0} {1} {0}_{1}".format(ph, model))

                # Move protonated model in right folder
                        os.system("mv {0}_{1} {2}/p_{3}".format(ph, model, p_models_path, rec))

                # Clean files
                        os.system("rm {0}_{1}.propka".format(ph, model))
                os.system("rm {0}".format(model))


end = time.time()
print(end - start)


