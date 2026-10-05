#!/usr/bin/env python3
# 把桌面壁纸上的旧名「月薪鸭」改成新商店名「打表上班」。
#
# 背景：App Store 上架名已定为「打表上班」，但 mac-1 用的那张桌面截图里，
# 壁纸正写着「月薪鸭」三个大字，同屏出现两个名字会让人困惑。
#
# 做法：文字区域用上下边界的像素做纵向线性插值填充（壁纸是极缓的暖灰白渐变，
# y=270 与 y=342 之间只差 2 个色阶，填完看不出接缝），再用苹方 Semibold 重写。
# 只动「月薪鸭」那一块，下面的说明文字原样保留。

import os
from PIL import Image, ImageDraw, ImageFont

PF = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc"
PF_SEMIBOLD = 11

SRC = ("/Users/borry5/Library/Mobile Documents/com~apple~CloudDocs/"
       "简历大作战/项目经历/iOS APP/月薪鸭/MoonSalary-docs/app-store/screenshots/"
       "mac-1280x800-panel.png")
DST = "/tmp/msrender-mac/panel-wallpaper-fixed.png"

OLD_TEXT = "月薪鸭"
NEW_TEXT = "打表上班"

# 「月薪鸭」实测 bbox：x 84..188、y 284..330（墨迹高 46px）
BOX = (70, 274, 300, 340)      # 覆盖区（含余量，给 4 个字留宽）
Y_TOP, Y_BOT = 270, 342        # 插值取样行（都在干净背景上）
INK = (26, 26, 31)
TARGET_H = 46                  # 原墨迹高度，用来反推字号
BASELINE_CX = 80               # 文字左起点，与原「月薪鸭」对齐
BASELINE_CY = 307              # 原文字垂直中心


def ink_height(font, text):
    """量出文字实际墨迹高度（不是行高）"""
    img = Image.new("L", (600, 200), 255)
    ImageDraw.Draw(img).text((20, 100), text, font=font, fill=0, anchor="lm")
    # 注意：getbbox() 判的是「非零」而非「非白」，白底 255 会把整张图算进去，
    # 必须先二值化成 文字=255 / 背景=0 再取包围盒
    mask = img.point(lambda v: 255 if v < 128 else 0)
    bbox = mask.getbbox()
    return bbox[3] - bbox[1] if bbox else 0


def pick_size():
    """找到墨迹高度最接近 TARGET_H 的字号"""
    best, best_d = None, 999
    for size in range(40, 80):
        f = ImageFont.truetype(PF, size, index=PF_SEMIBOLD)
        h = ink_height(f, OLD_TEXT)
        d = abs(h - TARGET_H)
        if d < best_d:
            best, best_d = size, d
    return best


def main():
    im = Image.open(SRC).convert("RGB")
    x0, y0, x1, y1 = BOX

    # 纵向线性插值填充
    px = im.load()
    for x in range(x0, x1):
        top = px[x, Y_TOP]
        bot = px[x, Y_BOT]
        span = Y_BOT - Y_TOP
        for y in range(y0, y1):
            t = (y - Y_TOP) / span
            px[x, y] = (
                round(top[0] + (bot[0] - top[0]) * t),
                round(top[1] + (bot[1] - top[1]) * t),
                round(top[2] + (bot[2] - top[2]) * t),
            )

    size = pick_size()
    f = ImageFont.truetype(PF, size, index=PF_SEMIBOLD)
    print(f"  字号 {size} → 墨迹高 {ink_height(f, OLD_TEXT)}px（目标 {TARGET_H}）")

    ImageDraw.Draw(im).text((BASELINE_CX, BASELINE_CY), NEW_TEXT,
                            font=f, fill=INK, anchor="lm")

    im.save(DST, "PNG")
    print(f"  {DST}  {im.size[0]}x{im.size[1]}")

    # 量一下新文字的实际范围，确认没越界
    g = im.convert("L")
    xs = [x for x in range(x0, x1) for y in range(y0, y1) if g.getpixel((x, y)) < 180]
    ys = [y for y in range(y0, y1) for x in range(x0, x1) if g.getpixel((x, y)) < 180]
    if xs:
        print(f"  新文字 bbox: x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}"
              f"  （覆盖区 x{x0}..{x1} y{y0}..{y1}）")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    main()
