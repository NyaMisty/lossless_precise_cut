import os
import sys
import subprocess
import json
import math
import shlex

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

if os.name == "nt":
    FFMPEG = os.path.join(application_path, "ffmpeg.exe")
    FFPROBE = os.path.join(application_path, "ffprobe.exe")
else:
    FFMPEG = os.path.join(application_path, "ffmpeg")
    FFPROBE = os.path.join(application_path, "ffprobe")

print("ffmpeg location: %s" % FFMPEG)

def getFrame(srcFile, t):
    output = subprocess.check_output([FFPROBE, '-select_streams', 'v', '-skip_frame', 'nokey', '-show_frames', '-show_entries', 'frame=pkt_pts_time,pict_type', '-read_intervals', '%.6f%%+%.6f' % (t - 20.0, 40.0), '-print_format', 'json', srcFile], stderr=subprocess.DEVNULL)
    ret = json.loads(output)
    #print(ret)
    last_key_frame = float(ret["frames"][0]["pkt_pts_time"])
    next_key_frame = float(ret["frames"][-1]["pkt_pts_time"])
    for c in ret["frames"]:
        cur = float(c["pkt_pts_time"])
        if cur <= t and cur > last_key_frame:
            last_key_frame = cur
        elif cur > t and cur < next_key_frame:
            next_key_frame = cur
    return last_key_frame, next_key_frame

def procexec(args):
    print("    Exec: [%s]" % subprocess.list2cmdline(args))
    subprocess.call(args, stderr=subprocess.DEVNULL)

ENCODING_OPT1 = ["-r", "60", "-video_track_timescale", "120", "-color_range", "tv", "-colorspace", "bt470bg", "-color_primaries", "bt709", "-color_trc", "1"]
ENCODING_OPT2 = ["-color_range", "tv", "-colorspace", "bt470bg", "-color_primaries", "bt709", "-color_trc", "1"]


def smartCut(srcFile, dstFile, startT, durationT, encode_arg=[]):
    # load I-frame time
    last_key_frame, next_key_frame = getFrame(srcFile, startT)
    before_end_frame, after_end_frame = getFrame(srcFile, startT + durationT)
    endT = startT + durationT
    print("Cutting: start %.6f, duration %.6f, end %.6f. Retrived keyframe: before_start %.6f, after_start %.6f, before_end %.6f, after_end %.6f" % (startT, durationT, endT, last_key_frame, next_key_frame, before_end_frame, after_end_frame))
    
    args = [FFMPEG, "-hide_banner", "-i", srcFile, "-vn", "-ss", "%.6f" % startT, "-t", "%.6f" % durationT, "-c:a", "copy", dstFile + "_a.m4a"]
    procexec(args)
    args = [FFMPEG, "-hide_banner", "-noaccurate_seek", "-ss", "%.6f" % last_key_frame, "-i", srcFile, "-t", "%.6f" % (next_key_frame - last_key_frame + 1), "-c", "copy", "-f", "segment", "-an", dstFile + "_head%d.ts"]
    procexec(args)
    args = [FFMPEG, "-hide_banner", "-i", dstFile + "_head%d.ts" % 0, "-ss", "%.6f" % (startT - last_key_frame), "-c:v", "libx264", "-copyts", *encode_arg, "-start_at_zero", "-x264opts", "stitchable", "-profile:v", "high", "-level", "5.0", "-crf", "18", dstFile + "_head.ts"]
    procexec(args)
    args = [FFMPEG, "-hide_banner", "-noaccurate_seek", "-ss", "%.6f" % next_key_frame, "-i", srcFile, "-to", "%0.6f" % (before_end_frame - next_key_frame), "-c", "copy", "-an", dstFile + "_main.ts"]
    #args = [FFMPEG, "-hide_banner", "-ss", "%.6f" % next_key_frame, "-i", srcFile, "-to", "%0.6f" % (before_end_frame - next_key_frame), "-c", "copy", "-an", dstFile + "_main.ts"]
    procexec(args)
    args = [FFMPEG, "-hide_banner", "-noaccurate_seek", "-ss", "%.6f" % before_end_frame, "-i", srcFile, "-t", "%.6f" % (after_end_frame - before_end_frame + 1), "-c", "copy", "-an", "-f", "segment", dstFile + "_tail%d.ts"]
    procexec(args)
    args = [FFMPEG, "-hide_banner", "-i", dstFile + "_tail%d.ts" % 0, "-t", "%.6f" % (endT - before_end_frame), "-c:v", "libx264", "-copyts", *encode_arg, "-start_at_zero", "-x264opts", "stitchable", "-profile:v", "high", "-level", "5.0", "-crf", "18", dstFile + "_tail.ts"]
    procexec(args)
    #args = [FFMPEG, "-hide_banner", "-copytb", "1", "-fflags", "+igndts", "-i", "concat:%s|%s|%s" % (dstFile + "_head.ts", dstFile + "_main.ts", dstFile + "_tail.ts"), "-c:v", "copy", "-an", "-fflags", "+genpts", dstFile + "_v.mp4"]
    args = [FFMPEG, "-hide_banner", "-copytb", "1", "-start_at_zero", "-i", "concat:%s|%s|%s" % (dstFile + "_head.ts", dstFile + "_main.ts", dstFile + "_tail.ts"), "-c:v", "copy", "-an", dstFile + "_v.mp4"]
    procexec(args)
    args = [FFMPEG, "-hide_banner", "-i", dstFile + "_v.mp4", "-i", dstFile + "_a.m4a", "-c", "copy", "-map", "0:0", "-map", "1:0", dstFile]
    procexec(args)
    for c in ["_a.m4a", "_head.ts", "_main.ts", "_tail.ts", "_v.mp4"] + ["_head%d.ts" % i for i in range(5)] + ["_tail%d.ts" % i for i in range(5)]:
        try:
            os.remove(dstFile + c)
            pass
        except:
            pass
    