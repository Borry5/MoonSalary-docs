#!/usr/bin/env python3
# 抹掉统计页底部的「跟大佬」区块（含马云 / 马化腾等真实人名）。
#
# 为什么必须处理：这是 App Store 展示图的源图之一，出现真实人物姓名有
# 肖像权 / 商标风险，审核容易被挑。
#
# 做法（比重画 tab bar 可靠得多）：
#   1. 把底部整片填成页面背景色 #F3F3F5
#   2. 再把 tab bar 胶囊区域的原像素按圆角遮罩贴回来
#
# 关键前提：实测「跟大佬」的文字在 x 110..245，落在胶囊（x 269..1050）
# 之外，胶囊内部只是垫着一张白卡片 —— 所以抠出来的胶囊是干净的，
# 不需要重画图标和文字。

import os
from PIL import Image, ImageDraw

SRC = ("/Users/borry5/Library/Mobile Documents/com~apple~CloudDocs/"
       "简历大作战/项目经历/iOS APP/月薪鸭/MoonSalary-docs/app-store/screenshots/"
       "iphone-6.9-2-stats.png")
DST = "/tmp/msrender-lock/stats-clean.png"

BG = (243, 243, 245)              # 页面背景色（实测）
FILL_TOP = 2555                   # 从这里往下整片填背景色

# tab bar 胶囊：由「顶部高光平直段 x 341..978」+ 圆角半径 72 反推
CAP = (269, 2615, 1050, 2760)     # left, top, right, bottom
CAP_RADIUS = 72

# home indicator（原图那条被卡片压住了，补一条）
HI = (460, 2838, 860, 2848)
HI_RADIUS = 5

# 胶囊内底色均值（压平用的目标色）
CAP_BASE = (248, 248, 248)


def main():
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    print(f"  源图 {W}x{H}")

    # 先把胶囊原样抠出来（带圆角遮罩，避免把圆角外的白卡片一起贴回）
    cap = im.crop(CAP)
    mask = Image.new("L", cap.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, cap.size[0] - 1, cap.size[1] - 1], radius=CAP_RADIUS, fill=255)
    cap_rgba = cap.convert("RGBA")
    cap_rgba.putalpha(mask)

    # 整片填背景色
    ImageDraw.Draw(im).rectangle([0, FILL_TOP, W, H], fill=BG)

    # 胶囊贴回
    im.paste(cap_rgba, (CAP[0], CAP[1]), cap_rgba)

    # 清掉胶囊内「跟大佬」的透字残影与卡片顶边。
    #
    # 胶囊是毛玻璃，底下的文字和白色卡片边缘都会淡淡透上来。试过用纯色矩形
    # 覆盖，但残影正好和「总览」的图标 / 文字叠在一起，矩形避不开。
    #
    # 改用「色调压平」：阈值区间 236..254 正好卡在三者之间（实测灰阶）——
    #   统计 tab 选中灰底  229..235  → 保留（真实的 UI 边界）
    #   「跟大佬」透字残影 237..245  → 压平
    #   胶囊底色          246..253  → 压平
    #   图标内纯白 ¥       255       → 保留
    # 残影消失，图标文字分毫不动。代价是胶囊底的抗锯齿边缘会窄 1..2px，肉眼不可辨。
    CLEAR = CAP
    region = im.crop(CLEAR).copy()
    rpx = region.load()
    for y in range(region.size[1]):
        for x in range(region.size[0]):
            r, g, b = rpx[x, y]
            if 236 <= (r + g + b) / 3 <= 254:
                rpx[x, y] = CAP_BASE

    # 按圆角遮罩贴回，避免把圆角外的背景也压平
    keep = Image.new("L", (W, H), 0)
    ImageDraw.Draw(keep).rounded_rectangle(
        [CAP[0], CAP[1], CAP[2] - 1, CAP[3] - 1], radius=CAP_RADIUS, fill=255)
    im.paste(region, (CLEAR[0], CLEAR[1]), keep.crop(CLEAR))

    # 补 home indicator
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(HI, radius=HI_RADIUS, fill=(255, 255, 255))

    im.save(DST, "PNG")
    print(f"  {DST}  {im.size[0]}x{im.size[1]}")

    # 复核：胶囊之外不该再有任何深色像素（人名、头像都是深色）
    # 胶囊内的图标本身就是黑色，要排除掉
    def in_cap(x, y):
        return CAP[0] <= x < CAP[2] and CAP[1] <= y < CAP[3]

    g = im.convert("L")
    dark = [(x, y) for y in range(FILL_TOP, H, 3) for x in range(0, W, 3)
            if g.getpixel((x, y)) < 150 and not in_cap(x, y)]
    print(f"  胶囊外深色像素数：{len(dark)}" + (f"  样例 {dark[:5]}" if dark else "  ✓ 干净"))


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    main()
