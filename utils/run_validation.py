import os
import sys
import argparse
import numpy as np
from desc.twinkles.validation import validation_pipeline

if __name__ == "__main__":

    file_descrip = 'Run Sprinkler Instance Catalog tests.'
    parser = argparse.ArgumentParser(description=file_descrip)

    parser.add_argument('cat_folder', type=str,
                        help='Filepath to the Instance Catalogs.')

    parser.add_argument('visit_num', type=int,
                        help='Visit number of the Instance Catalog.')

    parser.add_argument('sne_SED_path', type=str,
                        help=str('Filepath to the location of the folder/n' +
                                 'where the dynamic SNe SEDs are stored.'))

    args = parser.parse_args()
    cat_folder = args.cat_folder
    visit_num = args.visit_num
    sne_SED_path = args.sne_SED_path

    validation_pipeline(cat_folder, visit_num, sne_SED_path)
