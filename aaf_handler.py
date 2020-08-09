import os
import sys
import subprocess
import json
import math
import shlex

from cutter import *

def genOutName(name, num, newsuffix):
    n, _, suffix = name.rpartition('.')
    return "%s-%s.%s" % (n, num, newsuffix)
    
from timecode import Timecode
import aaf2
from aaf2.components import SourceClip

def handleAaf(aafpath, srcpath, outdir="."):
    with aaf2.open(aafpath, "r") as f:
        ff = []
        i = 0
        maincomp = next(f.content.toplevel())
        for seg in maincomp.slots[0].segment.slots[0].components:
            if not isinstance(seg, SourceClip):
                continue
            mainMobName = seg.mob.name
            mainMobRate = float(seg.mob.slots[0].edit_rate)
            start_t = (seg.start / mainMobRate + 0.005) # the float will get trimmed, so we have to plus some trivial time
            duration_t = (seg.length / mainMobRate)
            i += 1
            start_tc = str(Timecode(60, None, None, seg.start)).replace(":", ".")
            duration_tc = str(Timecode(60, None, None, seg.length)).replace(":", ".")
            out = genOutName(mainMobName, "%s_%s" % (start_tc, duration_tc), "mp4")
            if os.path.exists(out):
                print("%s already exists, ignoring" % out)
                continue
            smartCut(srcpath + "/" + mainMobName, os.path.join(outdir, out), start_t, duration_t)
            #break
            #ff.append(subprocess.Popen(args))
            #subprocess.call(args)
        
        for c in ff:
            c.join()

def main():
    if len(sys.argv) <= 2:
        print("Usage: python %s AAF_FILE_PATH CLIP_SOURCE_DIR" % sys.argv[0])
        return
    handleAaf(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()