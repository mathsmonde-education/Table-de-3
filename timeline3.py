import math
import random

FPS = 30
W, H = 270, 480
SCALE = 4

PINK = (247, 37, 133)
PURPLE = (114, 9, 183)
DBLUE = (58, 12, 163)
LBLUE = (67, 97, 238)
TURQ = (76, 201, 240)
WHITE = (255, 255, 255)
YELLOW = (255, 208, 40)
GOAL_GREENS = ((20, 120, 66), (26, 136, 76))
DARKBG = (6, 5, 20)

INTRO = 105
N_OPS = 10

PHASES_NORMAL = [("aim", 14), ("kick", 7), ("travel", 23), ("hit", 4),
                 ("explode", 16), ("result", 34), ("out", 6)]
PHASES_SAVE = [("aim", 14), ("kick", 7), ("travel", 23), ("hit", 4),
               ("save", 10), ("aim2", 10), ("kick2", 7), ("travel2", 20),
               ("explode", 16), ("result", 34), ("out", 6)]
SAVE_OP = 1

OPS_X = [100, 165, 90, 190, 120, 205, 78, 150, 105, 175]
GOAL_X1, GOAL_X2 = 52, 218
GOAL_Y1, GOAL_Y2 = 50, 140
KEEPER_Y = 143
PLAYER_Y = 408

FINALE = 280


def keeper_base(f):
    return 120 + 40 * math.sin(f * 0.045)


OPS = []
op_start = INTRO
for i in range(N_OPS):
    phases = PHASES_SAVE if i == SAVE_OP else PHASES_NORMAL
    starts = {}
    acc = 0
    for (name, dur) in phases:
        starts[name] = (op_start + acc, dur)
        acc += dur
    tx = OPS_X[i % len(OPS_X)]
    px = 135 + (tx - 135) * 0.55
    f_impact1 = starts["hit"][0]
    base_impact = keeper_base(f_impact1)
    cross = px + (tx - px) * ((PLAYER_Y - KEEPER_Y) / (PLAYER_Y - 118))
    dive_dir1 = -1 if cross >= base_impact else 1
    kd = {"cross": cross}
    if i == SAVE_OP:
        kd["amp1"] = cross - base_impact
        kd["catch_x"] = cross
        kd["catch_y"] = KEEPER_Y
        tx2 = cross - 75 if cross >= 135 else cross + 75
        tx2 = max(GOAL_X1 + 22, min(GOAL_X2 - 22, tx2))
        px2 = 135 + (tx2 - 135) * 0.55
        f_impact2 = starts["explode"][0]
        base_impact2 = keeper_base(f_impact2)
        kd["amp2"] = 54.0 if tx2 >= base_impact2 else -54.0
        kd["tx2"] = tx2
        kd["px2"] = max(30, min(240, px2))
    else:
        kd["amp1"] = 54.0 * dive_dir1
    OPS.append({"start": op_start, "total": acc, "starts": starts,
                "tx": tx, "px": max(30, min(240, px)),
                "keeper": kd})
    op_start += acc

TOTAL_OPS_END = op_start
FINALE_START = TOTAL_OPS_END
TOTAL = FINALE_START + FINALE


def phase_of(i, f):
    op = OPS[i]
    k = f - op["start"]
    for (name, dur) in (PHASES_SAVE if i == SAVE_OP else PHASES_NORMAL):
        if k < dur:
            return name, k, dur
        k -= dur
    return None, 0, 0


def goals_before(f):
    n = 0
    for i, op in enumerate(OPS):
        hit = op["starts"]["hit"]
        end_hit = hit[0] + hit[1]
        if i == SAVE_OP:
            if f >= op["starts"]["explode"][0]:
                n += 1
        elif f >= end_hit:
            n += 1
    return n


rng = random.Random(11)
FW_COLORS = [PINK, TURQ, LBLUE, PURPLE, (255, 220, 70), WHITE]
FINALE_FIREWORK = [8, 30, 46, 66, 88, 108, 126, 148, 168, 190, 212, 232, 252]
FIREWORKS = []
for k in range(len(FINALE_FIREWORK)):
    frame = FINALE_START + FINALE_FIREWORK[k] + rng.randint(0, 5)
    x = rng.randint(38, W - 38)
    y = rng.randint(65, 300)
    FIREWORKS.append((frame, x, y, FW_COLORS[k % len(FW_COLORS)]))

BURST_DUR = 52

sfx_events = []


def sfx_events():
    ev = []
    for i, op in enumerate(OPS):
        st = op["starts"]
        for kick in ("kick", "kick2"):
            if kick in st:
                ev.append((st[kick][0] / FPS, 'kick', i))
        hit0 = st["hit"][0]
        if i == SAVE_OP:
            ev.append((hit0 / FPS, 'save', i))
            ev.append((st["explode"][0] / FPS, 'goal', i))
        else:
            ev.append((hit0 / FPS, 'goal', i))
    ev.append(((INTRO - 6) / FPS, 'whistle', 0))
    ev.append((FINALE_START / FPS, 'fanfare', 0))
    for idx, (fr, x, y, c) in enumerate(FIREWORKS):
        ev.append((fr / FPS, 'pop', idx))
    return sorted(ev, key=lambda e: e[0])
