import math
import random
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw

from font5x7 import draw_text, text_w
from timeline3 import (DBLUE, FINALE, FINALE_START, FPS, GOAL_GREENS, GOAL_X1,
                       GOAL_X2, GOAL_Y1, GOAL_Y2, INTRO, KEEPER_Y, LBLUE,
                       N_OPS, OPS, PINK, PLAYER_Y, PURPLE, SCALE, TURQ, W, H,
                       TOTAL, WHITE, YELLOW, FIREWORKS, BURST_DUR, DARKBG,
                       goals_before, keeper_base, phase_of)

PLAYER_PINK, PLAYER_LBLUE = PINK, LBLUE
NET_DIM = (170, 190, 255)


def blend(c, f):
    return tuple(int(v * f) for v in c)


def draw_hud(dr, f):
    dr.rectangle([0, 0, W - 1, 21], fill=DBLUE)
    s = "MATHS MONDE"
    x = (W - text_w(s, 2)) // 2
    draw_text(dr, x, 4, s, WHITE, 2, shadow=(30, 8, 80))
    slick = int((f * 2.2) % (W + 8)) - 4
    if 0 <= slick < W:
        dr.rectangle([max(0, slick), 21, max(0, slick) + 2, 21], fill=PINK)
    dr.rectangle([0, 22, W - 1, 24], fill=PINK)
    dr.rectangle([0, 25, W - 1, 26], fill=TURQ)
    score = 100 * goals_before(f)
    sc = f"SCORE {score:05d}"
    draw_text(dr, W - 5 - text_w(sc, 1), 30, sc, WHITE, 1, shadow=(30, 30, 70))
    draw_text(dr, 5, 30, "TABLE DE 3", TURQ, 1, shadow=(10, 60, 60))


def draw_pitch(dr, f):
    dr.rectangle([0, 0, W - 1, 355], fill=DARKBG)
    for k in range(70):
        x = (int(k * 37.3) + f * 0) % W
        y = (k * 53) % 44
        dr.rectangle([x, y, x, y], fill=blend(PURPLE, 0.5 + 0.4 * math.sin(k + f * 0.1)))
    y0 = 44
    stripe = 0
    for yy in range(44, H, 40):
        dr.rectangle([0, yy, W - 1, min(H - 1, yy + 39)],
                     fill=GOAL_GREENS[stripe % 2])
        stripe += 1
    dr.rectangle([0, y0, 4, H - 1], fill=blend(TURQ, 0.8))
    dr.rectangle([W - 5, y0, W - 1, H - 1], fill=blend(TURQ, 0.8))
    ymid = 330
    dr.rectangle([5, ymid, W - 6, ymid], fill=blend(TURQ, 0.8))
    dr.ellipse([135 - 34, ymid - 34, 135 + 34, ymid + 34],
               outline=blend(TURQ, 0.8), width=1)
    dr.rectangle([78, 44, 192, 190], outline=blend(TURQ, 0.8), width=1)
    dr.rectangle([78, 44, 192, 84], outline=blend(TURQ, 0.8), width=1)


def draw_goal(dr, f):
    dr.rectangle([GOAL_X1, GOAL_Y1, GOAL_X2, GOAL_Y2], fill=(10, 8, 40))
    for gx in range(GOAL_X1 + 4, GOAL_X2, 9):
        dr.rectangle([gx, GOAL_Y1 + 2, gx, GOAL_Y2 - 2], fill=blend(NET_DIM, 0.30))
    for gy in range(GOAL_Y1 + 4, GOAL_Y2, 9):
        dr.rectangle([GOAL_X1 + 2, gy, GOAL_X2 - 2, gy], fill=blend(NET_DIM, 0.30))
    for px in (GOAL_X1 - 2, GOAL_X2):
        dr.rectangle([px, GOAL_Y1, px + 2, GOAL_Y2 + 2], fill=WHITE)
    dr.rectangle([GOAL_X1 - 2, GOAL_Y1 - 2, GOAL_X2 + 2, GOAL_Y1], fill=WHITE)
    dr.rectangle([GOAL_X1 - 4, GOAL_Y2 + 1, GOAL_X2 + 4, GOAL_Y2 + 3],
                 fill=TURQ)


def draw_operation(dr, i, f):
    op = OPS[i]
    st = op["starts"]
    visible = f >= st["aim"][0] and f < st["result"][0]
    if not visible:
        return None
    tw = text_w("3*4 = ?", 2)
    th = 14
    cx = (GOAL_X1 + GOAL_X2) // 2 - 6
    cy = (GOAL_Y1 + GOAL_Y2) // 2
    pulse = 1 if (f // 6) % 2 == 0 else 0
    col = TURQ if pulse else WHITE
    bw, bh = tw + 12, th + 8
    x0, y0 = cx - bw // 2, cy - bh // 2
    dr.rectangle([x0, y0, x0 + bw, y0 + bh], fill=(12, 10, 46),
                 outline=PINK)
    s = f"3*{i + 1} = ?"
    draw_text(dr, cx - tw // 2, cy - th // 2, s, col, 2, shadow=(0, 0, 0))
    return cx, cy


PLAYER_SCALE = 3
BALL_SCALE = 2


def draw_player(dr, f, px, py=None, kicking=False):
    s = PLAYER_SCALE
    ox = int(px) - 4 * s
    oy = ((py if py is not None else PLAYER_Y) - 5 * s)
    kick_ph = (f // 3) % 2 if kicking else -1
    for ry, row in enumerate(PLAYER_ROWS):
        for rx, ch in enumerate(row):
            if ch == '.':
                continue
            x0, y0 = ox + rx * s, oy + ry * s
            color = PINK
            if ch == 'H':
                color = (90, 50, 25)
            elif ch == 'S':
                color = LBLUE
            elif ch == 'K':
                color = (255, 220, 180)
            dr.rectangle([x0, y0, x0 + s - 1, y0 + s - 1], fill=color)
    if kicking:
        lx = ox + (s if kick_ph == 0 else 6 * s)
        dr.rectangle([lx, oy + 8 * s, lx + s + 1, oy + 11 * s + s - 1],
                     fill=(255, 220, 180))


PLAYER_ROWS = [
    "..HHHHH..",
    "..HHHHH..",
    "...HHH...",
    "PPPPPPPPP",
    "PPPSSSPPP",
    "PP.SSS.PP",
    "K..SSS..K",
    "...SSS...",
    "...S.S...",
    "...K.K...",
]


def draw_keeper(dr, f, i, op):
    kd = op["keeper"]
    st = op["starts"]
    kick1 = st["kick"][0]
    hit_end = st["hit"][0] + st["hit"][1]
    dx = 0.0
    if kick1 - 3 <= f < hit_end:
        p = (f - (kick1 - 3)) / max(1, hit_end - (kick1 - 3))
        dx = kd["amp1"] * math.sin(p * math.pi / 2)
    elif f >= hit_end:
        if i == 1:
            save_end = st["save"][0] + st["save"][1]
            kick2 = st["kick2"][0]
            explode_end2 = st["explode"][0] + st["explode"][1]
            if f < save_end:
                dx = kd["amp1"]
            elif f < kick2 - 3:
                r = min(1.0, (f - save_end) / 14)
                dx = kd["amp1"] * (1 - r)
            elif f < explode_end2:
                p = (f - (kick2 - 3)) / max(1, explode_end2 - (kick2 - 3))
                dx = kd["amp2"] * math.sin(p * math.pi / 2)
            else:
                r = min(1.0, (f - explode_end2) / 10)
                dx = kd["amp2"] * (1 - r)
        else:
            r = min(1.0, (f - hit_end) / 9)
            dx = kd["amp1"] * (1 - r)
    kx = int(keeper_base(f) + dx)
    ks = 3
    if abs(dx) > 6:
        ox, oy = kx - 6 * ks, KEEPER_Y - 2 * ks
        rows = KEEPER_DIVE
    else:
        ox, oy = kx - 3 * ks, KEEPER_Y - 3 * ks
        rows = KEEPER_ROWS
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            if ch == '.':
                continue
            color = YELLOW
            if ch == 'H':
                color = (60, 40, 15)
            elif ch == 'W':
                color = WHITE
            x0, y0 = ox + rx * ks, oy + ry * ks
            dr.rectangle([x0, y0, x0 + ks - 1, y0 + ks - 1], fill=color)
    return kx


KEEPER_ROWS = ["H.....H", "YYYYYYY", "YHYYYHY", "YYYYYYY", ".YYYYY.", ".W...W."]

KEEPER_DIVE = [
    "WYY......YYW",
    ".YYYHHHHYYY.",
    "..YYYYYYYY..",
    "....YYYY....",
]

EXPL_COLORS = [PINK, TURQ, LBLUE, PURPLE, WHITE, (255, 220, 70)]
GOAL_PARTS = []
for i in range(N_OPS):
    r = random.Random(2000 + i)
    parts = []
    for _ in range(30):
        parts.append((r.uniform(0, 2 * math.pi), r.uniform(0.6, 2.9),
                      r.choice(EXPL_COLORS), r.choice([1, 1, 2])))
    GOAL_PARTS.append(parts)

FW_PARTS = []
for i in range(len(FIREWORKS)):
    r = random.Random(500 + i)
    color = FIREWORKS[i][3]
    shades = [color, tuple(min(255, c + 80) for c in color), WHITE]
    parts = []
    for _ in range(40):
        parts.append((r.uniform(0, 2 * math.pi), r.uniform(0.5, 2.5),
                      r.choice(shades), r.choice([1, 1, 1, 2])))
    FW_PARTS.append(parts)

CONFETTI = []
r = random.Random(77)
for _ in range(50):
    CONFETTI.append((r.randint(0, W - 1), r.randint(0, 300),
                     r.uniform(0.5, 1.4),
                     r.choice(EXPL_COLORS), r.choice([1, 1, 2])))


def draw_ball(dr, bx, by, f):
    s = BALL_SCALE
    x0, y0 = int(bx) - 2 * s, int(by) - 2 * s
    dr.rectangle([x0, y0, x0 + 5 * s - 1, y0 + 5 * s - 1], fill=WHITE)
    ph = (f // 3) % 2
    if ph:
        dr.rectangle([x0 + s, y0 + s, x0 + 2 * s + 1, y0 + 2 * s + 1],
                     fill=(20, 20, 40))
    else:
        dr.rectangle([x0 + 2 * s, y0 + 2 * s, x0 + 2 * s + 1, y0 + 2 * s + 1],
                     fill=(20, 20, 40))
        dr.rectangle([x0, y0, x0 + 1, y0 + 1], fill=blend(WHITE, 0.7))


def ball_pos(op, phase, k, dur):
    tx = op["tx"] if phase != "travel2" else op["keeper"]["tx2"]
    px = op["px"] if phase in ("travel",) else (
        op["keeper"]["px2"] if phase == "travel2" else op["px"])
    ty = 118
    p = min(1.0, (k + 1) / dur)
    return px + (tx - px) * p, PLAYER_Y - 12 + (ty - (PLAYER_Y - 12)) * p


def draw_goal_fx(dr, i, k, tx):
    parts = GOAL_PARTS[i]
    for (ang, sp, col, sz) in parts:
        pxx = tx + int(math.cos(ang) * sp * k)
        pyy = 118 + int(math.sin(ang) * sp * k + k * k * 0.02)
        if 0 <= pxx < W and 0 <= pyy < H:
            c = blend(col, max(0.15, 1 - k / 18))
            dr.rectangle([pxx, pyy, pxx + sz, pyy + sz], fill=c)


def draw_result(dr, i, k):
    s = str(3 * (i + 1))
    tw = text_w(s, 3)
    cx = (GOAL_X1 + GOAL_X2) // 2
    col = WHITE if (k // 4) % 2 == 0 else TURQ
    bw, bh = tw + 12, 21 + 10
    x0, y0 = cx - bw // 2, 112 - bh // 2 + 18
    dr.rectangle([x0, y0, x0 + bw, y0 + bh], fill=(12, 10, 46), outline=TURQ)
    draw_text(dr, cx - tw // 2, y0 + 5, s, col, 3, shadow=(0, 40, 40))
    return x0, y0


def draw_goal_text(dr, k):
    if k > 40:
        return
    s = "GOAL!"
    sc = 4 if k > 2 else 3
    tw = text_w(s, sc)
    col = PINK if (k // 3) % 2 == 0 else WHITE
    draw_text(dr, (W - tw) // 2, 205, s, col, sc, shadow=(120, 0, 60))


def draw_fireworks(dr, f):
    for idx, (f0, fx, fy, col) in enumerate(FIREWORKS):
        if f0 - 10 <= f < f0:
            j = f - (f0 - 10)
            ry = fy + (10 - j) * 7
            c = blend(WHITE, 0.3 + 0.07 * j)
            dr.rectangle([fx, ry, fx + 1, ry + 2], fill=c)
        elif f0 <= f < f0 + BURST_DUR:
            k = f - f0
            for (ang, sp, c, sz) in FW_PARTS[idx]:
                px = fx + int(math.cos(ang) * sp * k)
                py = fy + int(math.sin(ang) * sp * k + k * k * 0.012)
                if 0 <= px < W and 0 <= py < H:
                    cc = blend(c, max(0.1, 1 - k / BURST_DUR))
                    dr.rectangle([px, py, px + sz, py + sz], fill=cc)


def draw_trophy(dr, ox, oy, sc):
    GOLD = (255, 208, 40)
    ORN = (205, 130, 0)
    WH = (252, 240, 200)
    bowl = [(2, 14), (2, 14), (2, 14), (3, 13), (4, 12), (6, 10), (7, 9)]
    for r, (a, b) in enumerate(bowl):
        for x in range(a, b + 1):
            col = ORN if x >= b - 1 else GOLD
            if 3 <= x <= 4 and 1 <= r <= 3:
                col = WH
            dr.rectangle([ox + x * sc, oy + r * sc,
                          ox + x * sc + sc - 1, oy + r * sc + sc - 1], fill=col)
    for r in range(1, 5):
        for x in (0, 16):
            dr.rectangle([ox + x * sc, oy + r * sc,
                          ox + x * sc + sc - 1, oy + r * sc + sc - 1], fill=GOLD)
    for r in range(7, 10):
        for x in (7, 8, 9):
            dr.rectangle([ox + x * sc, oy + r * sc,
                          ox + x * sc + sc - 1, oy + r * sc + sc - 1], fill=ORN)
    for x in range(4, 13):
        dr.rectangle([ox + x * sc, oy + 10 * sc,
                      ox + x * sc + sc - 1, oy + 10 * sc + sc - 1], fill=GOLD)
    for x in range(3, 14):
        dr.rectangle([ox + x * sc, oy + 11 * sc,
                      ox + x * sc + sc - 1, oy + 11 * sc + sc - 1], fill=ORN)


def scene_finale(dr, k, f):
    if k > FINALE - 90:
        for (cx0, y0, sp, col, sz) in CONFETTI:
            y = int((y0 + k * sp * 1.6) % (H + 10)) - 5
            x = int((cx0 + 12 * math.sin(k * 0.05 + y0))) % W
            dr.rectangle([x, y, x + sz - 1, y + sz - 1], fill=blend(col, 0.9))
    draw_fireworks(dr, f)
    if k < 6:
        sc = 2 if k < 3 else 6
    else:
        sc = 5
    s = "CHAMPION"
    tw = text_w(s, sc)
    bob = int(6 * math.sin(f * 0.09))
    col = PINK if (k // 8) % 2 == 0 else WHITE
    draw_text(dr, (W - tw) // 2, 78 + bob, s, col, sc, shadow=(60, 0, 90))
    ty = 250 + bob // 2
    draw_trophy(dr, (W - 17 * 4) // 2, ty, 4)
    s2 = "TABLE DE 3 REUSSIE"
    sx = (W - text_w(s2, 1)) // 2
    draw_text(dr, sx, 336 + bob // 3, s2, TURQ, 1, shadow=(10, 50, 50))
    py = PLAYER_Y - 8 - int(abs(10 * math.sin(f * 0.25)))
    draw_player(dr, f, 135, py=py, kicking=False)
    dr.rectangle([130, py + 14, 133, py + 17], fill=WHITE)


def smooth(p):
    return p * p * (3 - 2 * p)


def render_frame(f):
    img = Image.new('RGB', (W, H))
    dr = ImageDraw.Draw(img)
    if f < INTRO:
        draw_pitch(dr, f)
        draw_goal(dr, f)
        if f > 6:
            col = [PINK, TURQ, LBLUE][f % 3] if f < 14 else TURQ
            box_w, box_h = 168, 104
            bx0, by0 = (W - box_w) // 2, 190
            dr.rectangle([bx0, by0, bx0 + box_w, by0 + box_h],
                         fill=(12, 10, 46), outline=PURPLE)
            for li, s in enumerate(["TABLE", "DE 3"]):
                tw = text_w(s, 3)
                draw_text(dr, (W - tw) // 2, by0 + 12 + li * 40, s, col, 3,
                          shadow=(114, 9, 183))
        if f > 30 and (f // 10) % 2 == 0:
            s = "PRET ?"
            draw_text(dr, (W - text_w(s, 2)) // 2, 320, s, PINK, 2,
                      shadow=(80, 0, 40))
        py = int(500 - (500 - PLAYER_Y) * smooth(min(1.0, max(0.0, (f - 12) / 16))))
        draw_player(dr, f, 135, py, kicking=f > 12)
        draw_ball(dr, 135, py + 16 * PLAYER_SCALE - 8, f)
        draw_keeper(dr, f, 0, OPS[0])
        draw_hud(dr, f)
        return img

    if f < FINALE_START:
        i = next((j for j in range(N_OPS) if OPS[j]["start"] <= f < OPS[j]["start"] + OPS[j]["total"]), N_OPS - 1)
        op = OPS[i]
        st = op["starts"]
        name, k, dur = phase_of(i, f)
        draw_pitch(dr, f)
        draw_goal(dr, f)
        draw_operation(dr, i, f)
        player_px = op["px"]
        kicking = name in ("kick", "kick2")
        if name == "aim2":
            p = (k + 1) / dur
            start_px = op["keeper"]["catch_x"]
            player_px = start_px + (op["keeper"]["px2"] - start_px) * smooth(p)
        elif i == 1 and name in ("kick2", "travel2", "explode", "result", "out"):
            player_px = op["keeper"]["px2"]
        draw_player(dr, f, player_px, kicking=kicking)
        kx = draw_keeper(dr, f, i, op)
        if name in ("travel",):
            bx, by = ball_pos(op, name, k, dur)
            draw_ball(dr, bx, by, f)
        elif name in ("kick", "kick2"):
            draw_ball(dr, player_px, PLAYER_Y - 12, f)
        elif name == "hit":
            if i == 1:
                bx, by = kx, KEEPER_Y
                draw_ball(dr, bx, by, f)
                if k < 2:
                    dr.rectangle([0, 0, W - 1, H - 1], fill=blend(WHITE, 0.6))
            else:
                if k < 2:
                    dr.rectangle([0, 0, W - 1, H - 1], fill=blend(WHITE, 0.7))
        elif name == "save":
            p = (k + 1) / dur
            bx = op["keeper"]["catch_x"] + (op["keeper"]["catch_x"] - op["tx"]) * 0.25 * p
            by = KEEPER_Y + 70 * p
            draw_ball(dr, bx, by, f)
            s = "NON !"
            if (f // 4) % 2 == 0:
                draw_text(dr, (W - text_w(s, 2)) // 2, 240, s, PINK, 2,
                          shadow=(60, 0, 30))
        elif name in ("kick2", "travel2"):
            if name == "kick2" or (name == "travel2" and k < dur):
                bx, by = ball_pos(op, name, k, dur)
                draw_ball(dr, bx, by, f)
        elif name == "explode":
            kex = k + (st["hit"][1] if i != 1 else 4)
            draw_goal_fx(dr, i, k, op["tx"] if i != 1 else op["keeper"]["tx2"])
            if k < 2:
                dr.rectangle([0, 0, W - 1, H - 1], fill=blend(WHITE, 0.7))
        elif name == "result":
            draw_result(dr, i, k)
            draw_goal_text(dr, k)
            fy = 150 - min(14, int(k * 0.25))
            draw_text(dr, op["tx"] - text_w("+100", 1) // 2, fy, "+100", WHITE, 1,
                      shadow=(0, 0, 0))
        elif name == "out":
            draw_goal_text(dr, 40)
    else:
        scene_finale(dr, f - FINALE_START, f)
    draw_hud(dr, f)
    return img


def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    out = 'table_de_3_1080x1920.mp4'
    cmd = [ff, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0',
           '-i', 'music.wav',
           '-vf', f'scale={W * SCALE}:{H * SCALE}:flags=neighbor',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
           '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-shortest',
           '-movflags', '+faststart', out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    for f in range(TOTAL):
        proc.stdin.write(render_frame(f).tobytes())
    proc.stdin.close()
    proc.wait()
    err = proc.stderr.read()
    proc.stderr.close()
    if proc.returncode != 0:
        raise SystemExit(err.decode()[-3000:])
    print('done', out, TOTAL, 'frames')


if __name__ == '__main__':
    main()
