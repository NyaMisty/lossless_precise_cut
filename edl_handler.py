import os
import sys
import subprocess

def genOutName(name, num, newsuffix):
    n, _, suffix = name.rpartition('.')
    return "%s-%s.%s" % (n, num, newsuffix)

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def convertTc(tc):
    return rreplace(str(tc), ":", ".", 1)

from edl import Parser

def handleEdl(edlpath, srcpath, outdir):
    parser=Parser('60')
    with open(edlpath, encoding='gbk') as f:
        edl=parser.parse(f)
        ff = []
        i = 0
        for event in edl.events:
            print(event.__dict__)
            print("Event Number:"+str(event.num))
            print("Clip Name:"+str(event.clip_name))
            if event.clip_name is not None:
                i += 1
                out = genOutName(event.clip_name, "%s_%s" % (str(event.src_start_tc).replace(":", "."), str(event.src_end_tc).replace(":", ".")), "mp4")
                if os.path.exists(out):
                    print("%s already exists, ignoring" % out)
                    continue
                start_t = event.src_start_tc.frame_number / float(event.src_start_tc.framerate)
                end_t = event.src_end_tc.frame_number / float(event.src_start_tc.framerate)
                duration_t = end_t - start_t
                smartCut(srcpath + "/" + event.clip_name, os.path.join(outdir, out), start_t, duration_t)
                #break
                #ff.append(subprocess.Popen(args))
        for c in ff:
            c.join()
    

def main():
    if len(sys.argv) <= 2:
        print("Usage: python %s EDL_FILE_PATH CLIP_SOURCE_DIR" % sys.argv[0])
        return
    return handleEdl(sys.argv[1], sys.argv[0])
        

if __name__ == "__main__":
    main()