import os
import sys
import subprocess

def genOutName(name, num, newsuffix):
    n, _, suffix = name.rpartition('.')
    return "%s-%s.%s" % (n, num, newsuffix)

def main():
    if len(sys.argv) <= 3:
        print("Usage: python %s START_SEC END_SEC SRC_FILE" % sys.argv[0])
        return
    out = genOutName(event.clip_name, "%s_%s" % (str(event.src_start_tc).replace(":", "."), str(event.src_end_tc).replace(":", ".")), "mp4")
    if os.path.exists(out):
        print("%s already exists, ignoring" % out)
        continue
    start_t = float(sys.argv[1])
    end_t = float(sys.argv[2])
    duration_t = end_t - start_t
    smartCut(sys.argv[3], out, start_t, duration_t)


if __name__ == "__main__":
    main()