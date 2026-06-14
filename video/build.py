#!/usr/bin/env python3
"""Assemble the 1-minute Cipherfell narrated trailer.
Usage: py build.py --audio path/to/vo.mp3 [--out cipherfell_trailer.mp4]
Builds a Ken-Burns slideshow from game art timed to the voiceover, mixes a soft
CC0 BGM bed under the narration. Run from the project root or the video/ dir."""
import argparse, os, subprocess, sys, json, math
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
A = lambda p: os.path.join(ROOT, p)
VID = os.path.join(ROOT, "video"); FR = os.path.join(VID, "frames")
os.makedirs(FR, exist_ok=True)
W, H, FPS = 1920, 1080, 30

# storyboard: (image, weight) — weights distribute the voiceover duration
STORY = [
    ("assets/cover.webp",          1.05),
    ("assets/cine_night.webp",     1.15),
    ("assets/cine_baron.webp",     0.95),
    ("assets/cine_commission.webp",1.05),
    ("assets/npc_impostor.webp",   1.10),
    ("assets/prop_cipher.webp",    1.00),
    ("assets/prop_keyring.webp",   1.00),
    ("assets/prop_gossip.webp",    1.00),
    ("_shot_refined_square.png",   1.05),
    ("assets/cine_finale.webp",    1.30),
]
BGM = "assets/audio/bgm_cine.ogg"
XFADE = 0.0   # using fade-to-black between segments (robust)

def ffprobe_dur(path):
    out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nw=1:nk=1", path]).decode().strip()
    return float(out)

def make_frame(src, idx):
    im = Image.open(A(src)).convert("RGB")
    iw, ih = im.size; ar = iw/ih
    if 1.5 <= ar <= 1.95:  # ~16:9 -> cover-fill the whole frame
        s = max(W/iw, H/ih); nw, nh = int(iw*s), int(ih*s)
        big = im.resize((nw, nh), Image.LANCZOS)
        x, y = (nw-W)//2, (nh-H)//2
        canvas = big.crop((x, y, x+W, y+H))
    else:  # other aspect -> blurred cover background + contained foreground
        s = max(W/iw, H/ih); bg = im.resize((int(iw*s), int(ih*s)), Image.LANCZOS)
        bx, by = (bg.size[0]-W)//2, (bg.size[1]-H)//2
        bg = bg.crop((bx, by, bx+W, by+H)).filter(ImageFilter.GaussianBlur(34))
        bg = Image.eval(bg, lambda v: int(v*0.5))
        m = 0.86; fs = min(W*m/iw, H*m/ih); fw, fh = int(iw*fs), int(ih*fs)
        fg = im.resize((fw, fh), Image.LANCZOS)
        bg.paste(fg, ((W-fw)//2, (H-fh)//2)); canvas = bg
    out = os.path.join(FR, f"frame_{idx:02d}.png"); canvas.save(out); return out

def render_segment(frame, dur, idx, zoom_in=True):
    seg = os.path.join(FR, f"seg_{idx:02d}.mp4")
    df = max(1, int(round(dur*FPS)))
    if zoom_in:
        zp = f"zoompan=z='min(zoom+0.0009,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={df}:s={W}x{H}:fps={FPS}"
    else:
        zp = f"zoompan=z='if(eq(on,0),1.12,max(1.001,zoom-0.0009))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={df}:s={W}x{H}:fps={FPS}"
    fo = max(0.0, dur-0.45)
    vf = f"{zp},fade=t=in:st=0:d=0.45,fade=t=out:st={fo:.3f}:d=0.45,format=yuv420p"
    subprocess.run(["ffmpeg","-y","-loop","1","-i",frame,"-t",f"{dur:.3f}","-r",str(FPS),
        "-vf",vf,"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",seg],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seg

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--audio", required=True)
    ap.add_argument("--out", default=os.path.join(VID, "cipherfell_trailer.mp4"))
    args = ap.parse_args()
    vo_dur = ffprobe_dur(args.audio)
    print(f"voiceover duration: {vo_dur:.2f}s")
    total_w = sum(w for _, w in STORY)
    durs = [max(2.2, vo_dur*w/total_w) for _, w in STORY]
    # normalise so the slideshow exactly matches the voiceover length
    scale = vo_dur/sum(durs); durs = [d*scale for d in durs]
    segs = []
    for i, ((src, _), d) in enumerate(zip(STORY, durs)):
        fr = make_frame(src, i)
        segs.append(render_segment(fr, d, i, zoom_in=(i % 2 == 0)))
        print(f"  seg {i}: {src}  {d:.2f}s")
    # concat (all segments share codec/params)
    cat = os.path.join(FR, "concat.txt")
    with open(cat, "w") as f:
        for s in segs: f.write(f"file '{s}'\n")
    silent = os.path.join(FR, "silent.mp4")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",cat,"-c","copy",silent],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # mux: voiceover + soft looped BGM bed, fade BGM out at the end
    fo = max(0.0, vo_dur-2.0)
    filt = (f"[2:a]volume=0.10,afade=t=out:st={fo:.2f}:d=2.0[bg];"
            f"[1:a]volume=1.0[vo];[vo][bg]amix=inputs=2:duration=first:dropout_transition=3:normalize=0[mix];"
            f"[mix]loudnorm=I=-16:TP=-1.5:LRA=11[a]")
    subprocess.run(["ffmpeg","-y","-i",silent,"-i",args.audio,"-stream_loop","-1","-i",A(BGM),
        "-filter_complex",filt,"-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k",
        "-shortest",args.out], check=True)
    print("DONE ->", args.out, f"({ffprobe_dur(args.out):.2f}s)")

if __name__ == "__main__":
    main()
