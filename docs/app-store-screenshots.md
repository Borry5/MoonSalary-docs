# App Store 截图生成流程

本仓库 `app-store/screenshots/` 下的图都是这样生成出来的，可复现。

## 一、尺寸要求

| 用途 | 规格 | 数量 | 当前是否必需 |
|---|---|---|---|
| iPhone 6.9" | 1320 × 2868 | 3–10 | 备用 |
| **iPhone 6.5" 槽位** | **1284 × 2778** | 3–10 | **必需**（ASC 实际只给这个槽位） |
| iPhone 6.7" | 1290 × 2796 | 3–10 | 可选 |
| iPad 13" | 2064 × 2752 | 3–10 | **不再需要**（0.2.18 起 iPhone-only） |
| macOS | 1280 × 800 | 3–10 | **必需**（上架 Mac App Store 时） |

> ⚠️ **2026-10-06 实测更正**：App Store Connect 的 iPhone 截屏槽位标注为
> 「**6.5 英寸显示屏**」，明确只接受
> `1242 × 2688`、`2688 × 1242`、`1284 × 2778`、`2778 × 1284` 四个尺寸。
> **1320 × 2868 不在其中，拖进去会被拒。**
> 所以现在同时出两套：`1284 × 2778` 喂给这个槽位，`1320 × 2868` 备用。

模拟器实测：`iPhone 18 Pro Max` 出图正好 **1320 × 2868**；
`iPad Pro 13-inch (M5)` 出图正好 **2064 × 2752**。都不用再缩放。

## 一之二、成品在哪里

| 目录 | 内容 |
|---|---|
| `app-store/screenshots/` | **原始截图**（App 真实界面，未经排版） |
| `app-store/screenshots/asc/` | **营销排版成品**（品牌底色 + 卖点文案 + 圆角截图），直接上传用 |

> ⚠️ 原始截图里有**两张不可用**，别误用：
> - `iphone-6.9-3-profile.png` —— 顶部挂着「iCloud 不可用」错误横幅，版本号还是 0.2.18
> - `mac-1280x800-settings.png` —— 整张半透明重影（appearance 没钉 aqua 渲的），文字不可读
>
> 设置面板的可用版本由 `render-macos.swift` 重渲得到（见第三节）。
> 这两张暂时留在库里作为记录，**没有被任何展示图引用**。

`asc/` 下的命名：

```
iphone-6.9-1-lockscreen.png   1320×2868   锁屏小组件
iphone-6.9-2-overview.png     1320×2868   总览页
iphone-6.9-3-stats.png        1320×2868   统计页
iphone-6.5-*.png              1284×2778   同上三张，喂 6.5" 槽位
mac-1-menubar.png             1280×800    桌面实景 + 菜单栏面板
mac-2-settings.png            1280×800    设置面板
mac-3-value.png               1280×800    卖点卡片（为什么值得装）
```

macOS 槽位要求 **3–10 张**，所以 mac 那三张是齐的。三张各有分工：
1 给场景感（菜单栏常驻长什么样），2 展示可配置性，3 补价值主张。

> mac-3 之所以是纯排版的卖点卡片、而不是第三张界面截图：出图时是凌晨，
> 不在工作时段，实时进账算出来是 `0.0`、进度 `0%`，做展示图不好看；
> 而前两张已经把界面讲清楚了，第三张换成价值主张信息量更大。

## 一之三、营销排版怎么做的

纯 Python + Pillow（系统 `/usr/bin/python3` 自带 11.3.0）。要点：

- **中文卖点文案**用苹方 SC Semibold。**苹方不在 `/System/Library/Fonts/`**，
  在 `/System/Library/AssetsV2/com_apple_MobileAsset_Font8/<hash>.asset/AssetData/PingFang.ttc`。
  Pillow 索引：**3 = SC Regular、7 = SC Medium、11 = SC Semibold**
- 底色用柔和奶油渐变 `#FFF9EB → #FFE4A0`，深棕文字 `#2A2A00`。
  **别用饱和的琥珀 `#FFD65C → #EEA400`** —— 实测会压住截图，观感很吵
- 截图圆角 56px，先画一层高斯模糊的深色圆角矩形当投影，再贴图

### 两处源图修补（都在合成前做）

有两张源图不能直接用，需要先修：

**① `mac-1280x800-panel.png` 的壁纸写着旧名**

上架名定为「打表上班」，但那张桌面截图里壁纸正写着「月薪鸭」三个大字，
同屏出现两个名字会让人困惑。

修法：把文字区域用**上下边界的像素做纵向线性插值**填掉，再用苹方 Semibold 重写。
壁纸是极缓的暖灰白渐变（y=270 与 y=342 之间只差 2 个色阶），填完看不出接缝。
字号反推：原「月薪鸭」墨迹高 46px → 苹方 Semibold **49px** 正好对上。
下面的说明文字原样保留。

> 量文字墨迹高度时注意：`Image.getbbox()` 判的是「**非零**」而非「非白」，
> 白底 255 会把整张图算进去，必须先二值化成 文字=255 / 背景=0 再取包围盒。

**② `iphone-6.9-2-stats.png` 底部有真实人名**

统计页底部 tab bar 下方是「跟大佬」区块，列表项是**马云、马化腾**等真实人物。
出现在 App Store 展示图里有肖像权 / 商标风险，审核容易被挑。

修法（比重画 tab bar 可靠得多）：
1. 把底部整片填成页面背景色 `#F3F3F5`
2. 再把 tab bar 胶囊区域的原像素**按圆角遮罩贴回来**

关键前提：实测「跟大佬」的文字落在胶囊（x 269..1050）**之外**，
胶囊内部只是垫着一张白卡片 —— 所以抠出来的胶囊是干净的，不用重画图标文字。

但胶囊是**毛玻璃**，底下「跟大佬」的文字和卡片顶边仍会淡淡透上来。
残影是 237..245 的浅灰，与胶囊底色 246..253 几乎同色，矩形覆盖避不开
（正好和「总览」的图标叠在一起）。改用**色调压平**——把 236..254 的像素统一成底色：

| 灰阶区间 | 是什么 | 处理 |
|---|---|---|
| 229..235 | 统计 tab 选中灰底 | 保留（真实的 UI 边界） |
| 237..245 | 「跟大佬」透字残影 | 压平 |
| 246..253 | 胶囊底色 | 压平 |
| 255 | 图标里的纯白 ¥ | 保留 |

区间要卡准：下限放到 232 会啃掉选中灰底的下半部分，放到 220 会把整个灰底压平消失。

## 二、iPhone 截图

### 1. 构建到模拟器

```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
xcodebuild -project MoonSalary.xcodeproj -scheme MoonSalary -configuration Release \
  -destination 'generic/platform=iOS Simulator' -derivedDataPath /tmp/ms-asc-sim-dd \
  CODE_SIGNING_ALLOWED=NO \
  OTHER_SWIFT_FLAGS='$(inherited) -Xfrontend -disable-sandbox' build
```

### 2. 启动模拟器 + 摆好状态栏

App Store 的截图规范要求状态栏整洁，用 `status_bar override` 一步搞定：

```bash
UDID=7EC25A07-E212-4030-BDB6-6E6D7473354B   # iPhone 18 Pro Max
xcrun simctl boot $UDID
xcrun simctl status_bar $UDID override --time "9:41" \
  --batteryState charged --batteryLevel 100 \
  --cellularMode active --cellularBars 4 --wifiMode active --wifiBars 3
```

### 3. 播种界面数据（关键难点）

模拟器**点不了**，而薪资设置与工作记录存在 App Group 里。三种写法的实测结论：

| 写法 | 结果 |
|---|---|
| 直接改容器里的 `group.com.borry5.MoonSalary.plist` | ❌ **无效**。`plutil -p` 看着改了，app 读不到（cfprefsd 缓存 + 退出时回写） |
| `simctl spawn <udid> defaults write group.com.borry5.MoonSalary …` | ❌ `Domain not found` —— App Group 域在 app 容器里，不在模拟器全局偏好里 |
| `simctl spawn <udid> killall cfprefsd` | ❌ 模拟器 runtime 里**没有 `killall`**（No such file or directory） |
| **临时播种钩子 + 环境变量** | ✅ **唯一可行**，见下 |

做法：在 `MoonSalary/` 下加一个临时文件（自动同步目录，不用改 pbxproj），
在 `MoonSalaryApp.init()` 里按环境变量触发一次：

```swift
#if targetEnvironment(simulator)
// ⚠️ 临时验证代码（截图后立即移除）
enum ASCScreenshotSeed {
    static func applyIfNeeded() {
        guard ProcessInfo.processInfo.environment["MOON_ASC_SEED"] != nil else { return }
        // 写 dayOverrides.v1 / incomeSettings 到 AppGroupConfig.defaults
    }
}
#endif
```

```bash
SIMCTL_CHILD_MOON_ASC_SEED=1 xcrun simctl launch --console-pty $UDID borry5.MoonSalary
```

- `SIMCTL_CHILD_<VAR>` 前缀是 `simctl` 往 app 进程透传环境变量的机制
- **`--console-pty` 很关键**：不加的话 `launch` 会立刻返回，播种还没落盘就去截图了
- 用 `#if targetEnvironment(simulator)` 而不是 `#if DEBUG`（后者依赖工程设置，换工程就失效）

### 4. 切 tab + 截图

模拟器没有点击 API，用 `defaults write selectedTab` 切页（**写入时 app 必须正在运行**）：

```bash
xcrun simctl spawn $UDID defaults write borry5.MoonSalary selectedTab -int 0
sleep 4
xcrun simctl io $UDID screenshot /tmp/asc-shots/iphone-6.9-1-overview.png
```

顺序必须是「先 launch 再写」，反过来会把 app 切到后台，截到桌面。

### 5. 移除临时代码

```bash
rm -f MoonSalary/ZZTempASCScreenshotSeed.swift
git checkout -- MoonSalary/MoonSalaryApp.swift
grep -rnE "ASCScreenshotSeed|MOON_ASC_SEED" MoonSalary MoonWidget Shared   # 必须无输出
git status --porcelain --untracked-files=all                              # 必须为空
```

## 三、macOS 截图

`screencapture` 在这台机器上没有屏幕录制权限，改用**离屏渲染**：
把仓库源码复制到 `/tmp`、摘掉 `@main`，渲染成 PNG。

```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
SRC=<repo>
rm -rf /tmp/msrender-mac && mkdir -p /tmp/msrender-mac/src
cp "$SRC"/MoonSalary/*.swift "$SRC"/MoonSalary/Models/*.swift "$SRC"/MoonSalary/Views/*.swift /tmp/msrender-mac/src/
cp "$SRC"/Shared/*.swift /tmp/msrender-mac/src/
perl -pi -e 's/^\@main\s*$//' /tmp/msrender-mac/src/MoonSalaryApp.swift
```

`main.swift` 里渲染 `MainPanelView(store:)` / `SettingsPanelView(store:)`
（**注意这两个视图都要传 `store`**），编译时三个开关一个都不能漏：

```bash
xcrun -sdk macosx swiftc -O -swift-version 5 -target arm64-apple-macos13.0 \
  -Xfrontend -disable-sandbox \
  -Xfrontend -default-isolation -Xfrontend MainActor \
  -o /tmp/msrender-mac/render src/*.swift main.swift
```

### 渲染方式选型（实测结论）

| 方式 | TextField / 进度条 | 倍率控制 | 适用 |
|---|---|---|---|
| `ImageRenderer` | ❌ 渲成黄底 🚫 方块 | `.scale` 直接给 | 只能渲无输入控件、无进度条的界面 |
| `NSHostingView` + `cacheDisplay` | ✅ | 手动建 `NSBitmapImageRep` | 通用，但要补两处设置 |

**用 `NSHostingView` 必须补的两件事：**

**① 显式钉浅色外观**

```swift
host.appearance = NSAppearance(named: .aqua)
```

脱离窗口的 `NSHostingView` 解析不出 `effectiveAppearance`，动态色
（`.primary` / `.secondary`）会按**深色**外观取值 —— 浅色文字贴在白底上
整片看不见，看起来就像「半透明重影」。

> ⚠️ **更正**：早先把设置面板渲成半透明重影，归因为「撞上了视图的入场动画」。
> **这个判断是错的。** 真正的原因就是上面这条 appearance 没钉。
> 补上那一行之后，设置面板一次就渲干净了（TextField、Toggle、进度条全部正常）。
> 渲染前跑 RunLoop 等动画结束（settle）的写法仍然保留，但那是保险措施，不是必需的。

**② 给不画背景的视图补底色**

`SettingsPanelView` 自身不画背景 —— 真实场景里靠菜单栏面板的
`NSVisualEffectView` 材质层，离屏渲染时那层渲不出来，结果是**全透明**，
转 RGB 时会变成黑块。手动补 `#F2F2F7`（与 `MainPanelView` 渲出的底色一致）：

```swift
SettingsPanelView(store: store)
    .background(Color(red: 242 / 255, green: 242 / 255, blue: 247 / 255))
```

面板宽 300pt，2x 出图：主面板 600×974、设置面板 600×780。

**AppKit 离屏渲染的两个必踩坑**（都崩在 SIGTRAP / exit 133）：

1. **必须先 `_ = NSApplication.shared`**，否则字体与文字绘制会崩
2. **`NSGraphicsContext.current` 要在 `saveGraphicsState()` 之前设好**，顺序反了同样崩

### 合成

1280×800 的合成统一用 Pillow，不再走 AppKit —— 少一层崩溃面。

## 三之二、锁屏小组件截图（离屏渲染）

锁屏小组件是这个 App 的头号卖点，但**模拟器截不出来**：
`simctl` 没有把小组件装到锁屏的 API，模拟器也点不了。所以改用
**SwiftUI `ImageRenderer` 离屏渲染整套锁屏**。

思路：整张锁屏（壁纸渐变 + 9:41 + 日期 + 小组件 + 底部手电/相机按钮）
都在 SwiftUI 里搭出来，逻辑尺寸 440×956、`renderer.scale = 3`，
一次渲染正好 **1320×2868**。小组件的字号/字重/颜色严格照搬
`MoonWidget/IncomeWidget.swift` 的 `lockScreenView`：

```swift
Text(amount)
    .font(.system(size: 24, weight: .heavy, design: .rounded))
    .foregroundColor(.white)
    .monospacedDigit()
```

**这里用 `ImageRenderer` 而不是 `NSHostingView` + `cacheDisplay`，是因为锁屏里没有输入控件：**

- `ImageRenderer` 直接给 `.scale`，出图倍率可控，不用手动摆 `NSBitmapImageRep`
- 不用碰 `NSGraphicsContext.current` 与 `saveGraphicsState()` 的顺序坑（顺序反了崩 exit 133）
- 锁屏里既没有 `TextField` 也没有进度条，正好避开 `ImageRenderer` 渲不了这两者的短板

> 这里原本写的理由是「不会撞上视图的入场动画」—— **那是误判**，
> 真正原因是 appearance 没钉成浅色，见上一节的更正。

编译（三个开关一个都不能漏）：

```bash
xcrun -sdk macosx swiftc -O -swift-version 5 -target arm64-apple-macos13.0 \
  -Xfrontend -disable-sandbox \
  -Xfrontend -default-isolation -Xfrontend MainActor \
  -o /tmp/msrender-lock/render app-store/tools/render-lockscreen.swift
```

⚠️ **`ImageRenderer` 渲染不了 `TextField`，也渲染不了进度条** —— 两者都会渲成黄底带 🚫 的方块。
含输入控件或进度条的界面（设置面板、主面板）不能走这条路，
要用 `NSHostingView` + 钉 `appearance = .aqua`。

## 四、演示数据说明

截图里的数据是**播种出来的**，用 App 自带的默认值：

| 项 | 值 |
|---|---|
| 薪资来源 | 按月 ¥5654 |
| 工作日方案 | 双休（含调休） |
| 工作时段 | 09:00 – 18:00 |
| 10 月记录 | 10-01 / 10-02 加班 ×3，10-05 加班 ×2，10-09 加班 ×1.5，10-14 请假半天，10-22 加班 ×2 |

之所以给 10-05 记加班：截图当天（2026-10-05）是国庆假期，
不记加班的话英雄卡是「今天休息 ¥0.0」，看不出「实时进账」这个卖点。

## 五、工具链

全部入库在 `app-store/tools/`，按执行顺序：

| 脚本 | 作用 | 依赖 |
|---|---|---|
| `fix-wallpaper.py` | 抹掉 `mac-1280x800-panel.png` 壁纸上的旧名，改写为「打表上班」 | 源图 |
| `fix-stats.py` | 抹掉 `iphone-6.9-2-stats.png` 底部「跟大佬」区块（含真实人名） | 源图 |
| `render-lockscreen.swift` | 离屏渲染整套锁屏（含小组件）→ 1320×2868 | 独立，不依赖主仓源码 |
| `render-macos.swift` | 离屏渲染 macOS 主面板 / 设置面板 | 需先按第三节拷 `src/*.swift` |
| `compose-iphone.py` | iPhone 营销排版 → 6.9" 三张 + 6.5" 三张 | 前两个的输出 |
| `compose-macos.py` | macOS 营销排版 → 三张 | `render-macos.swift` 的输出 |

**完整重跑顺序**：

```bash
cd <MoonSalary-docs>
/usr/bin/python3 app-store/tools/fix-wallpaper.py
/usr/bin/python3 app-store/tools/fix-stats.py
# 渲染（先按第三节把主仓源码拷到 /tmp/msrender-mac/src）
cd /tmp/msrender-mac && ./render /tmp/msrender-mac 1.5
cd /tmp/msrender-lock && ./render /tmp/msrender-lock
# 合成
/usr/bin/python3 app-store/tools/compose-iphone.py
/usr/bin/python3 app-store/tools/compose-macos.py
```

脚本里的路径是**绝对路径硬编码**（含中文目录名），换机器要改开头那几个常量。

**成品验收**：

```bash
cd app-store/screenshots/asc
/usr/bin/python3 -c "
from PIL import Image; import glob, os
for f in sorted(glob.glob('*.png')):
    im = Image.open(f); print(f'{f:32s} {im.size[0]}x{im.size[1]}  {im.mode}')
"
```

必须全部是 `RGB`（**不能带 alpha**，App Store 会拒），且尺寸落在
`1284×2778` / `1320×2868` / `1280×800` 三个规格里。
