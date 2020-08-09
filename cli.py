import os
import sys
from edl_handler import handleEdl
from aaf_handler import handleAaf

def main():
    cutfile = input("AAF/EDL file: ")
    srcdir = input("Source dir: ")
    outdir = os.path.dirname(cutfile)
    input("Going to encode into output dir %s, continue? " % outdir)
    if cutfile.lower().endswith("aaf"):
        handleAaf(cutfile, srcdir, outdir)
    elif cutfile.lower().endswith("edl"):
        handleEdl(cutfile, srcdir, outdir)
    else:
        print("Unsupported file format!")
        sys.stdin.read(1)
        return
    print()
    print("Finished! Press any key to close")
    sys.stdin.read(1)

if __name__ == "__main__":
    main()