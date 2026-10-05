# 技术架构

## 仓库拓扑

```
月薪鸭/
├── code/
│   ├── MoonSalary/            # 主工作树，分支 feat/macos-settings-bubble
│   └── MoonSalary-release/    # 发布工作树，分支 release
└── MoonSalary-docs/           # 本仓库（文档 + GitHub Pages）
```

两个工作树各自独立构建，DerivedData 分别放 `/tmp/ms-dd-*` 与 `/tmp/msrel-dd-*`。
**注意不要用落后那份去点 Run**，会把设备打回旧代码。

## 工程结构

单 `xcodeproj`、单 scheme（`MoonSalary`），`SUPPORTED_PLATFORMS = "iphoneos iphonesimulator macosx"`，
一套代码同时产出 iOS 与 macOS 两端的 App。

| Target | Bundle ID | 说明 |
|---|---|---|
| `MoonSalary` | `borry5.MoonSalary` | 主 App，iOS + macOS |
| `MoonWidgetExtension` | `borry5.MoonSalary.MoonWidget` | 锁屏小组件，**仅 iOS** |

### 平台分支

代码里用 `#if os(iOS)` / `#if os(macOS)` 分流。两条 `#if` 紧邻在修饰符链中间会打断语法，
必须合并成一个 `#if`，或把平台分支包进独立视图。

### 目录

```
MoonSalary/          # 主 App（fileSystemSynchronizedRootGroup，增删文件不用改 pbxproj）
  ContentView.swift  # 根 TabView（总览 / 统计 / 我的）
  Views/             # TodayView / StatsView / ProfileView / ...
  Models/
MoonWidget/          # 小组件扩展（同样自动同步）
Shared/              # 双 target 共享，**手工登记在 pbxproj 里**，新增文件必须改 pbxproj
```

> `Shared/` 下的文件不属于自动同步目录。新增 `.swift` 要手动补齐 pbxproj 四处：
> `PBXBuildFile` / `PBXFileReference` / group children / Sources phase。
> 而且这些文件**不能引用 app target 独有符号**，否则 widget 编不过。

## 关键设计约束

### 存档兼容是红线

iCloud KV 存的是全量 JSON。**删字段或改枚举 `rawValue` 会让旧端解码整体失败、静默回退默认值。**
只能新增可选字段。`WorkdayScheme` 的 `rawValue`（"双休" / "大小周" / "单休"）是存档键，
界面文案一律走 `displayName`，两者不可混用。

### 小组件平台限制

`accessoryRectangular` / `accessoryInline` **在 macOS 上 unavailable**（编译直接报错）。
macOS 侧必须保留一个合法 family（`[.systemSmall, .systemMedium]`）才能编过。

让扩展只在 iOS 嵌入，靠 pbxproj 里 Embed Foundation Extensions 那个 `PBXBuildFile` 上的
`platformFilter = ios;`（旧写法 `platformFilters = (ios, )` 会被 Xcode 规范化成前者）。

**验证必须看产物，编译通过什么都说明不了：**

```bash
ls "<macOS app>/Contents/PlugIns"   # 期望：No such file or directory
ls "<iOS app>/PlugIns"              # 期望：有 MoonWidgetExtension.appex
```

### 部署目标

| | iOS | macOS |
|---|---|---|
| 主 App | 26.5 | 12.0 |
| 小组件 | 26.5 | 14.0 |

macOS 12 没有 `openWindow` / `.sensoryFeedback` / `SMAppService`，
建窗口要用 AppDelegate + NSWindow，开机自启要按系统版本分流。

## 数据流

```
用户输入 ──▶ IncomeSettings（薪资 / 工作日 / 工作时段）
                │
                ├──▶ 本机 UserDefaults + App Group
                │
                └──▶ NSUbiquitousKeyValueStore（用户自己的 iCloud 私有空间）
                          │
                          ▼
                IncomeCalculator ──▶ 实时金额
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   TodayView        MoonWidget        菜单栏 statusItem
  （iOS / macOS）    （iOS 锁屏）        （macOS）
```

节假日数据：`HolidayService` 从公开数据集拉取（jsDelivr → GitHub 原始地址两级回退），
按年缓存到本地，请求只带年份。

## 外观

- 品牌色：`MoonDesign.brand = #FFC730`，`brandDeep = #E8A400`
- 0.1.52 起外观固定「浅色极简」，底色跟随系统深浅色
- 只显示金额 + 状态，主题底色 / 祝福语 / 装饰环已全部移除

## 已冻结的功能（不要复活入口）

| 版本 | 冻结内容 | 恢复方式 |
|---|---|---|
| 0.2.14 | 摸鱼 / 加班模式：全平台下线入口与前端页面 | 逻辑代码保留在 `MoonSalaryApp.swift`，含恢复片段注释 |
| 0.2.15 | 小组件主屏 / 桌面 family；App 内「小组件」tab | `IncomeWidget.supportedFamilies` 加回 family；`ContentView` 放回 tag 1 |
| 0.2.16 | 「去下载 macOS 版」导流弹窗 | `ContentView.macPromoEnabled` 改回 `true`，**且必须先把 URL 换成 Mac App Store 链接** |
