"""Build the project page's teaser: a multi-material print and a drop, side by side.

    python docs/static/make_teaser.py fetch     # the two source clips into /tmp/teaser-src (82 MB)
    python docs/static/make_teaser.py render    # videos/teaser.mp4 and images/teaser.jpg
    python docs/static/make_teaser.py contact   # screenshots/teaser_storyboard.jpg, to check the cut

Needs ffmpeg with libx264 and the DejaVu Sans font. Both sources are already in
this repository, on the branches of PR #84 (the IDETC-CIE 2026 talk) and PR #86
(the drop-test protocol), so nothing is downloaded from YouTube.

Left panel: the build-chamber timelapse of a T3 prism printing on the Bambu Lab
H2D, PLA struts (black) and TPU tendons (orange) in one job. It is the talk's
16 s cut of YouTube nQNmi-NiL5I, sped up 1.6 times.

Right panel: the same kind of prism (specimen prc1kn) dropped from 60 in on the
drop-tower carriage, filmed at 959 frames per second and played at 30, so 32
times slower than real time. This drop, onto five felt pads in July 2026,
predates the optimization campaign (campaign drops land on polyurethane).
"""
import pathlib
import subprocess
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path("/tmp/teaser-src")
RAW = "https://github.com/vertical-cloud-lab/tensegrity-optimization/raw"
SOURCES = {
    # name: (commit, path in the repo)
    "print.mp4": ("e08f890", "presentation/media/clip-print-timelapse.mp4"),
    "drop.mp4": ("011c8e1", "data/drop-tests/prc1kn-60in-5felt/video/prc1kn_video1_slomo.mp4"),
}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

W, H, GAP = 1280, 720, 8           # output frame and the gap between panels
PW = (W - GAP) // 2                # each panel is 636 x 720
DUR = 10.0                         # seconds; both panels run the whole time
PRINT_SPEED = 1.6                  # the 16.04 s talk clip in 10.0 s
PRINT_X = 242                      # crop of the 1120 x 720 timelapse: tower and prism
DROP_START = 3.3                   # the carriage enters the frame at 3.5 s, lands at 7.6 s
DROP_Y = 300                       # crop of the 1080 x 1920 slow-motion clip
DROP_H = round(1080 * H / PW)      # 1223 px tall, the panel's 636:720 shape
POSTER_T = 4.4                     # the prism just after impact, in the teaser's time
FADE = 0.4


def fetch():
    SRC.mkdir(exist_ok=True)
    for name, (commit, path) in SOURCES.items():
        url = f"{RAW}/{commit}/{path}"
        print("fetch", url)
        urllib.request.urlretrieve(url, SRC / name)


def label(text):
    return (f"drawtext=fontfile={FONT}:text='{text}':x=16:y=h-th-20:fontsize=26:"
            "fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=10")


def render():
    out = HERE / "videos" / "teaser.mp4"
    poster = HERE / "images" / "teaser.jpg"
    out.parent.mkdir(exist_ok=True)
    poster.parent.mkdir(exist_ok=True)
    graph = ";".join([
        f"[0:v]setpts=PTS/{PRINT_SPEED},fps=30,crop={PW}:{H}:{PRINT_X}:0,"
        f"trim=duration={DUR},setpts=PTS-STARTPTS,setsar=1,"
        + label("3D printing PLA + TPU (timelapse)") + "[l]",
        f"[1:v]trim=start={DROP_START}:duration={DUR},setpts=PTS-STARTPTS,fps=30,"
        f"crop=1080:{DROP_H}:0:{DROP_Y},scale={PW}:{H}:flags=lanczos,setsar=1,"
        + label("Drop test (32x slow motion)") + "[r]",
        f"color=c=black:s={W}x{H}:r=30:d={DUR}[bg]",
        "[bg][l]overlay=0:0[a]",
        f"[a][r]overlay={PW + GAP}:0,"
        f"fade=t=in:st=0:d={FADE},fade=t=out:st={DUR - FADE}:d={FADE},format=yuv420p[v]",
    ])
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", str(SRC / "print.mp4"), "-i", str(SRC / "drop.mp4"),
        "-filter_complex", graph, "-map", "[v]", "-an", "-t", str(DUR),
        "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(out)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(POSTER_T), "-i", str(out),
                    "-frames:v", "1", "-q:v", "3", str(poster)], check=True)
    print(out, out.stat().st_size // 1000, "kB;", poster)


def contact():
    shots = HERE / "screenshots"
    shots.mkdir(exist_ok=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", str(HERE / "videos" / "teaser.mp4"),
        "-vf", "fps=0.8,scale=640:-2,tile=4x2:padding=6:color=white", "-frames:v", "1",
        "-q:v", "3", str(shots / "teaser_storyboard.jpg")], check=True)


if __name__ == "__main__":
    {"fetch": fetch, "render": render, "contact": contact}[sys.argv[1]]()
