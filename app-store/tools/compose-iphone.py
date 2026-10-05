#!/usr/bin/env python3
# App Store 展示图合成：品牌色背景 + 中文卖点文案 + 圆角截图
# 字体：苹方 SC（AssetsV2 里），SF 数字用系统渲染好的截图，无需另配

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PF = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc"
PF_SEMIBOLD = 11   # PingFang SC Semibold
PF_MEDIUM = 7      # PingFang SC Medium

SRC = "/Users/borry5/Library/Mobile Documents/com~apple~CloudDocs/简历大作战/项目经历/iOS APP/月薪鸭/MoonSalary-docs/app-store/screenshots"
LOCK = "/tmp/msrender-lock/lockscreen.png"
STATS_CLEAN = "/tmp/msrender-lock/stats-clean.png"
OUT = os.path.join(SRC, "asc")

BG_TOP = (255, 249, 235)
BG_BOTTOM = (255, 228, 160)
INK = (58, 42, 0)
SHADOW = (150, 110, 30, 95)


def font(size, index=PF_SEMIBOLD):
    return ImageFont.truetype(PF, size, index=index)


def gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line(
            [(0, y), (w, y)],
            fill=(
                round(top[0] + (bottom[0] - top[0]) * t),
                round(top[1] + (bottom[1] - top[1]) * t),
                round(top[2] + (bottom[2] - top[2]) * t),
            ),
        )
    return img


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, im.size[0] - 1, im.size[1] - 1], radius=radius, fill=255
    )
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def draw_centered(d, text, cx, cy, f, fill, spacing=None):
    """多行文本，每行水平居中，整体垂直居中于 cy"""
    lines = text.split("\n")
    asc, desc = f.getmetrics()
    lh = spacing or int((asc + desc) * 1.18)
    total = lh * len(lines)
    y = cy - total / 2
    for ln in lines:
        d.text((cx, y + lh / 2), ln, font=f, fill=fill, anchor="mm")
        y += lh


def build_iphone(src, headline, out_name, canvas=(1320, 2868)):
    W, H = canvas
    img = gradient((W, H), BG_TOP, BG_BOTTOM).convert("RGBA")
    d = ImageDraw.Draw(img)

    head_h = 430
    draw_centered(d, headline, W // 2, head_h // 2, font(80), INK)

    sw = 1100
    sh = round(sw * H / W)
    sx = (W - sw) // 2
    sy = 430
    if sy + sh > H - 30:
        sh = H - 30 - sy
        sw = round(sh * W / H)
        sx = (W - sw) // 2

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [sx, sy + 16, sx + sw, sy + sh + 16], radius=56, fill=SHADOW
    )
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(26)))

    shot = Image.open(src).convert("RGB").resize((sw, sh), Image.LANCZOS)
    img.paste(rounded(shot, 56), (sx, sy), rounded(shot, 56))

    out = os.path.join(OUT, out_name)
    img.convert("RGB").save(out, "PNG")
    print(f"  {out_name}  {img.size[0]}x{img.size[1]}")
    return out


def build_mac(src, out_name, canvas=(1280, 800)):
    W, H = canvas
    img = gradient((W, H), BG_TOP, BG_BOTTOM).convert("RGBA")

    shot = Image.open(src).convert("RGB")
    sw = 1152
    sh = round(sw * shot.size[1] / shot.size[0])
    if sh > 720:
        sh = 720
        sw = round(sh * shot.size[0] / shot.size[1])
    sx = (W - sw) // 2
    sy = (H - sh) // 2
    shot = shot.resize((sw, sh), Image.LANCZOS)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [sx, sy + 12, sx + sw, sy + sh + 12], radius=26, fill=SHADOW
    )
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(20)))
    img.paste(rounded(shot, 26), (sx, sy), rounded(shot, 26))

    out = os.path.join(OUT, out_name)
    img.convert("RGB").save(out, "PNG")
    print(f"  {out_name}  {img.size[0]}x{img.size[1]}")
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    print("=== iPhone 6.9\" (1320×2868) ===")
    jobs = [
        (LOCK, "锁屏一眼\n今天赚了多少", "iphone-6.9-1-lockscreen.png"),
        (os.path.join(SRC, "iphone-6.9-1-overview.png"), "把月薪\n换算成每一秒", "iphone-6.9-2-overview.png"),
        # 统计页用清理过的版本：原图底部 tab bar 下方是「跟大佬」区块，
        # 带马云 / 马化腾等真实人名，展示图里出现有肖像权风险。
        # 见 fix_stats.py —— 已把该区块抹掉、tab bar 原样保留。
        (STATS_CLEAN, "加班请假\n一笔都不落", "iphone-6.9-3-stats.png"),
    ]
    made = []
    for src, head, name in jobs:
        if not os.path.exists(src):
            print(f"  !! 缺源文件 {src}")
            continue
        made.append(build_iphone(src, head, name))

    print("=== iPhone 6.5\" 槽位 (1284×2778) ===")
    for f in made:
        im = Image.open(f)
        small = im.resize((1284, 2778), Image.LANCZOS)
        name = os.path.basename(f).replace("6.9", "6.5")
        p = os.path.join(OUT, name)
        small.save(p, "PNG")
        print(f"  {name}  {small.size[0]}x{small.size[1]}")

    # macOS 三张由 mac_extra.py 负责（含壁纸旧名修补），这里不再重复生成
    print("=== macOS 交由 mac_extra.py ===")


if __name__ == "__main__":
    main()
