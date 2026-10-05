# App Store 截图生成流程

本仓库 `app-store/screenshots/` 下的图都是这样生成出来的，可复现。

## 一、尺寸要求

| 用途 | 规格 | 数量 | 当前是否必需 |
|---|---|---|---|
| iPhone 6.9" | 1320 × 2868 | 3–10 | **必需** |
| iPhone 6.7" | 1290 × 2796 | 3–10 | 可选（有 6.9" 即可） |
| iPad 13" | 2064 × 2752 | 3–10 | **不再需要**（0.2.18 起 iPhone-only） |
| macOS | 1280 × 800 / 1440 × 900 / 2560 × 1600 / 2880 × 1800 | 3–10 | **必需**（上架 Mac App Store 时） |

模拟器实测：`iPhone 18 Pro Max` 出图正好 **1320 × 2868**；
`iPad Pro 13-inch (M5)` 出图正好 **2064 × 2752**。都不用再缩放。

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
把仓库源码复制到 `/tmp`、摘掉 `@main`，用 `NSHostingView` + `cacheDisplay` 渲染成 PNG。

```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
SRC=<repo>
rm -rf /tmp/msrender-mac && mkdir -p /tmp/msrender-mac/src
cp "$SRC"/MoonSalary/*.swift "$SRC"/MoonSalary/Models/*.swift "$SRC"/MoonSalary/Views/*.swift /tmp/msrender-mac/src/
cp "$SRC"/Shared/*.swift /tmp/msrender-mac/src/
perl -pi -e 's/^\@main\s*$//' /tmp/msrender-mac/src/MoonSalaryApp.swift
```

`main.swift` 里渲染 `MainPanelView(store: IncomeStore.shared)`（**注意这两个视图都要传 `store`**），
编译时三个开关一个都不能漏：

```bash
xcrun -sdk macosx swiftc -O -swift-version 5 -target arm64-apple-macos13.0 \
  -Xfrontend -disable-sandbox \
  -Xfrontend -default-isolation -Xfrontend MainActor \
  -o /tmp/msrender-mac/render src/*.swift main.swift
```

面板宽 300pt，2x 出图是 600×974。要凑成 1280×800 需要**合成**：
画一层渐变背景 + 顶部菜单栏条 + 右侧状态项，再把面板缩放挂到状态项下方。

合成用 AppKit 时两个必踩的坑：

1. **必须先 `_ = NSApplication.shared`**，否则字体与文字绘制会崩（SIGTRAP / exit 133）
2. **`NSGraphicsContext.current` 要在 `saveGraphicsState()` 之前设好**，
   顺序反了同样崩在 133

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
