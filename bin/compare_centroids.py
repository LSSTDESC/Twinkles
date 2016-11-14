import argparse
from desc.twinkles import CentroidValidator

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Read in an InstanceCatalog and a centroid file. "
                                     "Use CatSim to calculate the pixel positions of "
                                     "objects in the InstanceCatalog.  Compare this "
                                     "to the pixel positions as reported in the "
                                     "centroid file.\n\nexample:\n\n"
                                     "python compare_centroids.py --cat myInstanceCatalog.txt "
                                     "--cent myCentroidFile.txt --out_dir my/output/director/")

    parser.add_argument("--cat", type=str, help="path to the InstanceCatalog", default=None)
    parser.add_argument("--cent", type=str, help="path to the centroid file", default=None)
    parser.add_argument("--clean", type=bool, help="delete old files, if names conflict",
                        default=False)
    parser.add_argument("--out_dir", type=str, help="directory where we will put output files",
                        default=".")

    args = parser.parse_args()

    if args.cat is None or args.cent is None:
        raise RuntimeError("Must specify an InstanceCatalog and a centroid file.\n"
                           "You specified %s and %s" % (args.cat, args.cent))


    validator = CentroidValidator(args.cat, args.cent)
    validator.create_tex_file(args.out_dir, args.clean)
    print validator.get_scalars()
