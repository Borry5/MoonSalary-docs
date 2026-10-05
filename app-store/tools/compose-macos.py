#!/usr/bin/env python3
# macOS 展示图补齐：把 mac 槽位从 1 张补到 3 张。
#
#   mac-2-settings.png  设置面板（NSHostingView 重渲，修掉了半透明重影）
#   mac-3-panels.png    主面板 + 设置面板 并排
#
# 配色与 iPhone 那批一致：奶油渐变底 + 深棕字。

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PF = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc"
PF_SEMIBOLD = 11
PF_MEDIUM = 7

DOCS = "/Users/borry5/Library/Mobile Documents/com~apple~CloudDocs/简历大作战/项目经历/iOS APP/月薪鸭/MoonSalary-docs"
OUT = os.path.join(DOCS, "app-store/screenshots/asc")

PANEL = "/tmp/msrender-mac/panel-hosted.png"
SETTINGS = "/tmp/msrender-mac/settings.png"

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
        d.line([(0, y), (w, y)], fill=(
            round(top[0] + (bottom[0] - top[0]) * t),
            round(top[1] + (bottom[1] - top[1]) * t),
            round(top[2] + (bottom[2] - top[2]) * t),
        ))
    return img


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, im.size[0] - 1, im.size[1] - 1], radius=radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def draw_centered(d, text, cx, cy, f, fill, spacing=None):
    lines = text.split("\n")
    asc, desc = f.getmetrics()
    lh = spacing or int((asc + desc) * 1.18)
    y = cy - lh * len(lines) / 2
    for ln in lines:
        d.text((cx, y + lh / 2), ln, font=f, fill=fill, anchor="mm")
        y += lh


def paste_shot(canvas, src, w, h, x, y, radius):
    """把截图缩放到 (w,h) 贴到 (x,y)，带投影 + 圆角"""
    W, H = canvas.size
    shot = Image.open(src).convert("RGB").resize((w, h), Image.LANCZOS)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [x, y + 12, x + w, y + h + 12], radius=radius, fill=SHADOW)
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(20)))

    r = rounded(shot, radius)
    canvas.paste(r, (x, y), r)


def build_settings(out_name="mac-2-settings.png"):
    """设置面板：居中 + 上方文案"""
    W, H = 1280, 800
    img = gradient((W, H), BG_TOP, BG_BOTTOM).convert("RGBA")
    d = ImageDraw.Draw(img)

    draw_centered(d, "月薪 日薪 时薪\n三口径一处联动", W // 2, 92, font(46), INK)

    sh = 600
    sw = round(sh * 300 / 390)
    sx = (W - sw) // 2
    sy = 168
    paste_shot(img, SETTINGS, sw, sh, sx, sy, 22)

    out = os.path.join(OUT, out_name)
    img.convert("RGB").save(out, "PNG")
    print(f"  {out_name}  {W}x{H}  shot={sw}x{sh}")


def build_panels(out_name="mac-3-value.png"):
    """卖点卡片图。
    不用主面板截图：凌晨不在工作时段，实时进账算出来是 0.0、进度 0%，
    做展示图不好看；前两张已充分展示界面，这张补价值主张。"""
    W, H = 1280, 800
    img = gradient((W, H), BG_TOP, BG_BOTTOM).convert("RGBA")
    d = ImageDraw.Draw(img)

    draw_centered(d, "为什么值得装", W // 2, 88, font(48), INK)

    cards = [
        ("01", "菜单栏常驻", "不占 Dock、不占桌面，随时都在"),
        ("02", "实时进账", "抬眼扫一下，就知道今天赚到哪了"),
        ("03", "三口径联动", "月薪 / 日薪 / 时薪 自动换算"),
        ("04", "数据只在你手里", "不采集、不上传，iCloud 自己同步"),
    ]

    cw, ch = 520, 230
    gapx, gapy = 40, 40
    x0 = (W - (cw * 2 + gapx)) // 2
    y0 = 176

    for i, (num, title, desc) in enumerate(cards):
        cx = x0 + (i % 2) * (cw + gapx)
        cy = y0 + (i // 2) * (ch + gapy)

        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle(
            [cx, cy + 10, cx + cw, cy + ch + 10], radius=28, fill=SHADOW)
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))

        d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=28,
                            fill=(255, 255, 255, 255))

        pad = 44
        d.text((cx + pad, cy + pad - 6), num, font=font(26, PF_MEDIUM),
               fill=(232, 160, 32))
        d.text((cx + pad, cy + pad + 34), title, font=font(38), fill=INK)
        d.text((cx + pad, cy + pad + 104), desc, font=font(22, PF_MEDIUM),
               fill=(154, 136, 96))

    out = os.path.join(OUT, out_name)
    img.convert("RGB").save(out, "PNG")
    print(f"  {out_name}  {W}x{H}  cards={len(cards)}")


def build_menubar(out_name="mac-1-menubar.png"):
    """桌面 + 菜单栏面板（实景）。
    源图用修补过的版本：壁纸上的旧名「月薪鸭」已改成「打表上班」
    （见 fix_wallpaper.py），否则展示图里会同屏出现两个名字。"""
    W, H = 1280, 800
    img = gradient((W, H), BG_TOP, BG_BOTTOM).convert("RGBA")

    src = "/tmp/msrender-mac/panel-wallpaper-fixed.png"
    sw, sh = 1152, 720
    sx, sy = (W - sw) // 2, (H - sh) // 2
    paste_shot(img, src, sw, sh, sx, sy, 26)

    out = os.path.join(OUT, out_name)
    img.convert("RGB").save(out, "PNG")
    print(f"  {out_name}  {W}x{H}  shot={sw}x{sh}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("=== macOS ===")
    build_menubar()
    build_settings()
    build_panels()
