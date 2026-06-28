#!/usr/bin/env bash
# visualizar.sh — Renders EA output as a video of champion mesh frames.
#
# Usage (all arguments optional):
#   ./visualizar.sh [INPUT] [OUTPUT] [FPS] [STEP]
#
#   INPUT   saved EA output file; if omitted, the algorithm is run first
#   OUTPUT  video filename          (default: malha.mp4)
#   FPS     frames per second       (default: 25)
#   STEP    use every Nth iteration (default: 1, i.e. all frames)
#
# Dependencies: ffmpeg, matplotlib (pip install matplotlib)
#
# Examples:
#   ./visualizar.sh                           # run + render all frames
#   ./visualizar.sh output.txt                # render from saved file
#   ./visualizar.sh output.txt malha.mp4 10 5 # 10 fps, every 5th iteration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT="${1:-}"
OUTPUT="${2:-malha.mp4}"
FPS="${3:-25}"
STEP="${4:-1}"

# ── dependency checks ────────────────────────────────────────────────────────
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "error: ffmpeg not found — install with: sudo apt install ffmpeg" >&2
    exit 1
fi

if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

if ! python3 -c "import matplotlib" 2>/dev/null; then
    echo "error: matplotlib not found — install with: pip install matplotlib" >&2
    exit 1
fi

# ── optionally run the algorithm ─────────────────────────────────────────────
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

if [ -z "$INPUT" ]; then
    echo "Running algoritmo-evolucionario…"
    INPUT="$WORK/ea_output.txt"
    algoritmo-evolucionario > "$INPUT"
    echo "Algorithm finished."
fi

# ── parse output and render PNG frames ───────────────────────────────────────
FRAMES="$WORK/frames"
mkdir -p "$FRAMES"

echo "Parsing $INPUT…"

python3 - "$INPUT" "$FRAMES" "$STEP" <<'PYEOF'
import sys, re, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

input_path = sys.argv[1]
frames_dir = sys.argv[2]
step       = int(sys.argv[3])

# ── parse ─────────────────────────────────────────────────────────────────────
# Output format:
#   ##aptidão:X                    initial fitness (double #)
#   <coord lines>                  initial mesh
#   #iteração N / #aptidão X / … / <coord lines> / #---   per iteration
frames    = []   # list of (label, coord_lines)
state     = 'header'
curr_iter = None
curr_apt  = None
buf       = []   # accumulates non-comment coordinate lines

def flush(label):
    if buf:
        frames.append((label, list(buf)))
        buf.clear()

with open(input_path) as f:
    for raw in f:
        line = raw.rstrip()

        m = re.match(r'##aptidão:(.+)', line)
        if m:
            curr_apt = m.group(1).strip()
            continue

        m = re.match(r'#iteração\s+(\d+)', line)
        if m:
            flush(f"malha inicial  (aptidão {curr_apt})")
            state, curr_iter, curr_apt = 'iteration', int(m.group(1)), None
            buf.clear()
            continue

        m = re.match(r'#aptidão\s+(.+)', line)
        if m and state == 'iteration':
            curr_apt = m.group(1).strip()
            continue

        if line.startswith('#---') and state == 'iteration':
            apt_str = f"{float(curr_apt):.10f}" if curr_apt else '?'
            flush(f"iteração {curr_iter:>4d}   aptidão = {apt_str}")
            state = 'between'
            continue

        if line.startswith('#') or not line.strip():
            continue

        buf.append(line)

print(f"Parsed {len(frames)} frames.", flush=True)

# ── select frames ─────────────────────────────────────────────────────────────
n   = len(frames)
idx = sorted({0, *range(1, n - 1, step), n - 1}) if n > 1 else [0]
print(f"Rendering {len(idx)} frames (step={step})…", flush=True)

# ── set up a reusable figure ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 6))
fig.patch.set_facecolor('white')
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)
ax.set_aspect('equal')
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
for sp in ax.spines.values():
    sp.set_linewidth(0.5)

line_obj = None  # Line2D, created once and updated in place

def make_polyline(coord_lines):
    """Convert per-cell coordinate lines into a single x/y array with NaN breaks."""
    pts     = np.array([[float(v) for v in l.split()] for l in coord_lines])
    n_cells = len(pts) // 5
    cells   = pts[: n_cells * 5].reshape(n_cells, 5, 2)
    sep     = np.full((n_cells, 1, 2), np.nan)
    flat    = np.concatenate([cells, sep], axis=1).reshape(-1, 2)
    return flat[:, 0], flat[:, 1]

for out_i, src_i in enumerate(idx):
    label, coord_lines = frames[src_i]
    xs, ys = make_polyline(coord_lines)

    if line_obj is None:
        (line_obj,) = ax.plot(xs, ys, color='steelblue', linewidth=0.7)
    else:
        line_obj.set_data(xs, ys)

    ax.set_title(label, fontsize=9, pad=6)
    fig.savefig(os.path.join(frames_dir, f"frame_{out_i:05d}.png"),
                dpi=100, bbox_inches='tight')

    if (out_i + 1) % 100 == 0 or out_i + 1 == len(idx):
        print(f"  {out_i + 1}/{len(idx)}", flush=True)

plt.close(fig)
print("Frames done.", flush=True)
PYEOF

# ── assemble video ────────────────────────────────────────────────────────────
echo "Encoding → $OUTPUT  (${FPS} fps)…"
ffmpeg -y -loglevel warning \
    -framerate "$FPS" \
    -i "$FRAMES/frame_%05d.png" \
    -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" \
    -c:v libx264 -pix_fmt yuv420p -crf 18 \
    "$OUTPUT"

echo "Done → $OUTPUT"
