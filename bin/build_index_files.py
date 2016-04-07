"""
Script to generate a set of astrometry.net index files from a phosim
instance catalog.
"""
from __future__ import absolute_import, print_function
from builtins import range
import os
import shutil
import glob
import subprocess

def instcat_to_astrometry_net_input(instcat, ref_file='ref.txt'):
    """
    Convert a phosim instance catalog to a FITS file in the form of a
    binary table, retaining just the objects with a "starSED".

    @return The file name of the FITS file.
    """
    output = open(ref_file, 'w')
    output.write('#id RA DEC r starnotgal\n')
    for line in open(instcat):
        tokens = line.split()
        if tokens[0] != 'object' or not tokens[5].startswith('starSED'):
            continue
        output.write('%s %s %s %s 1\n' % tuple(tokens[1:5]))
    output.close()
    outfile = ref_file.replace('.txt', '.fits')
    command = "text2fits.py %(ref_file)s %(outfile)s -f 'kdddj'" % locals()
    subprocess.call(command, shell=True)
    os.remove(ref_file)
    return outfile

def build_index_files(ref_file, index_id, max_scale_number=4, output_dir='.'):
    """
    Generate astrometry.net index files from a reference file of stars.
    """
    file_ext = '%(index_id)s00' % locals()
    index_file_00 = 'index-%(file_ext)s.fits' % locals()
    index_files = [index_file_00]
    command = 'build-astrometry-index -i %(ref_file)s -o %(index_file_00)s -I %(file_ext)s -P 0 -S r -n 100 -L 20 -E -j 0.4 -r 1 > build-00.log' % locals()
    print(command)
    subprocess.call(command, shell=True)
    for scale_number in range(1, max_scale_number+1):
        file_ext = '%(index_id)s%(scale_number)02i' % locals()
        index_file = 'index-%(file_ext)s.fits' % locals()
        command = 'build-astrometry-index -1 %(index_file_00)s -o %(index_file)s -I %(file_ext)s -P %(scale_number)i -S r -L 20 -E -M -j 0.4 > build-%(scale_number)02i.log' % locals()
        print(command)
        subprocess.call(command, shell=True)
        index_files.append(index_file)
    if output_dir != '.':
        try:
            os.makedirs(output_dir)
        except OSError:
            pass
        for item in index_files:
            shutil.move(item, os.path.join(output_dir, item))
        for item in glob.glob('build-??.log'):
            shutil.move(item, os.path.join(output_dir, item))

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Script to generate astrometry.net index files from a phosim instance catalog")
    parser.add_argument('instcat', help='phosim instance catalog')
    parser.add_argument('index_id', help='id for index files')
    parser.add_argument('--max_scale_number', type=int, default=4, 
                        help='maximum scale_number for index files')
    parser.add_argument('--output_dir', type=str, default='.',
                        help='output directory')

    args = parser.parse_args()
    ref_file = instcat_to_astrometry_net_input(args.instcat)
    build_index_files(ref_file, args.index_id,
                      max_scale_number=args.max_scale_number,
                      output_dir=args.output_dir)
