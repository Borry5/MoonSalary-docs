# 上架合规清单与风险点

## 一、已完成项

| 项 | 状态 | 位置 |
|---|---|---|
| 隐私清单 `PrivacyInfo.xcprivacy` | ✅ 已加（主 App + Widget 各一份） | `MoonSalary/`、`MoonWidget/` |
| 出口合规声明 | ✅ `ITSAppUsesNonExemptEncryption = NO` | `project.pbxproj` app target 的 Debug/Release |
| 无追踪声明 | ✅ `NSPrivacyTracking = false` | 两份隐私清单 |
| required-reason API 声明 | ✅ 仅 `UserDefaults`（`CA92.1`） | 两份隐私清单 |
| macOS App Sandbox | ✅ `ENABLE_APP_SANDBOX = YES` | `project.pbxproj` |
| macOS Hardened Runtime | ✅ `ENABLE_HARDENED_RUNTIME = YES` | `project.pbxproj` |
| 无第三方 SDK / 无广告 / 无埋点 | ✅ 已全量扫描确认 | — |
| 隐私政策页面 | ✅ 中英双语 | `privacy/` |
| 技术支持页面 | ✅ 含 FAQ | `support/` |
| App 图标 1024×1024 | ✅ 已有 | `MoonSalary/Assets.xcassets/AppIcon.appiconset/icon_1024.png` |

## 二、已识别并处理的风险

### 1. App 内导流到 App Store 之外 ⚠️ 已处理

**问题**：iOS 端有一个「去下载 macOS 版」弹窗，按钮指向
`https://github.com/Borry5/MoonSalary`，而该仓库是 **private**——
用户点进去只会看到 404。更严重的是，「引导用户去 App Store 之外下载 App」
违反 App Store 审核指南。

**处理**：0.2.16 起冻结该弹窗入口（`ContentView.macPromoEnabled = false`），
视图与逻辑一行未删。

**恢复条件**：macOS 版上架拿到 `apps.apple.com` 链接后，
**必须先把 URL 换成 Mac App Store 的商店页**，再打开开关。

### 2. macOS 端读取主板 UUID ⚠️ 需留意审核口径

**位置**：`Shared/ICloudSync.swift` 的 `ioPlatformUUID`

**行为**：macOS 端读 `IOPlatformExpertDevice` 的 `IOPlatformUUID`，
拼上 macOS 用户名后 SHA-256 哈希，作为 iCloud 设备名录里的设备指纹。
iOS 端用的是 Apple 官方的 `identifierForVendor`。

**风险评估**：

- 不是序列号，是主板平台 UUID
- 有哈希，不可逆
- 只写入用户自己的 iCloud 私有空间，不上传开发者
- 只用于「在设备名录里区分是哪台设备」，不用于追踪

**结论**：属于合理的 App 功能，不是追踪。但审核员若追问，需按
`app-store/review-notes.md` 里的口径答复。

**待验证**：沙盒下的 macOS App 能否正常读到 `IOPlatformUUID`。
代码已有降级路径（读不到就退回 `hw.model` 机型标识），所以不会崩，
但设备名录里可能出现两台 Mac 显示成同一台的情况。**建议在装到
Mac App Store 版本后实测一次。**

### 3. 节假日数据走第三方 CDN ℹ️ 已披露

请求 `cdn.jsdelivr.net` 与 `raw.githubusercontent.com` 获取公开节假日数据集，
只带年份、不带用户信息。已在隐私政策第 3 节完整披露。

**注意**：`raw.githubusercontent.com` 在中国大陆可达性不稳定，
主源用 jsDelivr 是对的。若审核环境访问不了，App 会退回内置缓存。

### 4. iOS 部署目标 26.5 —— 影响可安装范围 ❗️需确认

`IPHONEOS_DEPLOYMENT_TARGET = 26.5`。

这不是合规问题，但直接决定**能装这个 App 的用户有多少**：
所有停留在 iOS 26.0 ~ 26.4 的设备都装不了。

**请确认这是有意为之。** 如果只是开发时随手设的，
建议降到 26.0 甚至 18.0，能覆盖的用户面大得多——
当前代码里用到的 API（`onChange` 无参版、`contentTransition`、
`presentationDetents` 等）都有更低版本的门槛，降低部署目标需要逐个加可用性判断，
工作量中等但收益明显。

### 5. iPad 支持已下线 ℹ️ 0.2.18 决策

`TARGETED_DEVICE_FAMILY` 从 `"1,2"` 改为 `"1"`，**只保留 iPhone**。

**原因**：iPadOS 18+ 会把根 `TabView` 适配成顶部分段式 tab 栏，
内容被挤进左侧约 228pt 的窄栏，右侧大片留白、文字截断
（实测「月薪 ¥5654 · 日…」被切掉），布局是坏的。

**决策**：与其临时修一套 iPad 布局，不如先只上 iPhone。
日后要恢复 iPad，需要重新设计 iPad 版根导航（改用 `NavigationSplitView`
或针对 `horizontalSizeClass == .regular` 单独排版），不是改一行配置的事。

**连带收益**：App Store 不再要求提交 iPad 13" 截图。

## 三、提交审核前待办

- [ ] **在 Xcode 登录 Apple ID**（Settings → Accounts，团队 `3CKSH29X7T`）
      —— 这是导出 / 上传的硬阻塞，目前本机只有 Apple Development 证书，
      没有 Apple Distribution 分发证书
- [ ] 归档 iOS，`-exportArchive` 导出 ipa
- [ ] 归档 macOS，导出 pkg
- [ ] 上传（把 `ExportOptions.plist` 的 `destination` 从 `export` 改成 `upload`）
- [ ] 在 App Store Connect 创建 App 记录（Bundle ID `borry5.MoonSalary`）
- [ ] 填 `app-store/metadata.md` 里的全部文案
- [ ] 上传截图（iPhone 6.9" ✅ 3 张已备；**iPad 已不再需要**；macOS ✅ 2 张，
      建议再补一张凑满 3 张）
- [ ] 填「App 隐私」问卷（选「不收集数据」，见 `app-store/privacy-answers.md`）
- [ ] 填年龄分级问卷（见 `app-store/age-rating.md`）
- [ ] 填审核备注（见 `app-store/review-notes.md`）
- [ ] 确认定价与分发范围
- [ ] 决定是否调整 iOS 部署目标（见风险 4）
- [ ] （代码待办）工作日请假时金额归零、但状态文案仍显示「搬砖中 / 下班！」，
      与 0.2.17 修掉的加班日 bug 同根因（`statusText` 与 `currentEarnings` 不同源）

## 四、关于截图

0.2.18 起 `TARGETED_DEVICE_FAMILY = "1"`，**只支持 iPhone**，
所以 **iPad 13" 截图不再是必填项**。

| 平台 | 是否必填 | 当前已备 |
|---|---|---|
| iPhone 6.9"（1320×2868） | ✅ 必填 | 3 张 |
| iPhone 6.7"（1290×2796） | 可复用 6.9" 素材 | — |
| iPad 13"（2064×2752） | ❌ 不再需要 | — |
| macOS（1280×800 起） | ✅ 必填（≥3 张） | 2 张，**建议补 1 张** |

尺寸表与生成流程见 `docs/app-store-screenshots.md`，
成品在 `app-store/screenshots/`。
