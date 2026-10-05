# 发布流程（打包 → 签名 → 上传 App Store）

本文记录月薪鸭从改完代码到上传 App Store Connect 的完整链路，命令均已实测。

## 0. 前置条件

| 条件 | 检查方式 |
|---|---|
| Xcode 完整安装（非 CommandLineTools） | `xcode-select -p` 输出 `/Applications/Xcode.app/Contents/Developer` |
| Xcode 已登录开发者账号 | Xcode → Settings → Accounts，团队 `3CKSH29X7T` |
| 有 Apple Distribution 证书 | `security find-identity -v -p codesigning` 里能看到 |
| 有 App Store 描述文件 | 首次导出时由 Xcode 自动创建 |

**如果 `security find-identity -v -p codesigning` 只有 `Apple Development`，
导出会失败并报 `error: exportArchive No Accounts`。** 这不是代码问题，
先让 Xcode 登录 Apple ID（会自动补发 Apple Distribution 证书与 App Store 描述文件）。
**完整图文步骤见 [`docs/app-store-connect-api-key.md`](app-store-connect-api-key.md)。**

> 只想让 `xcodebuild` 自动管理签名与证书，还可以给命令加
> `-authenticationKeyPath` / `-authenticationKeyID` / `-authenticationKeyIssuerID`
> 三个参数走 App Store Connect API Key，就不依赖 Xcode 里登录的账号。
> 这三个值怎么来，同样见 [`docs/app-store-connect-api-key.md`](app-store-connect-api-key.md)。

## 1. 版本号约定

- `MARKETING_VERSION` 只递增第三位（`0.2.17` → `0.2.18`），**绝不跳 0.2.x**
- 每次改代码都要 bump，且与代码改动**在同一个提交里**
- `CURRENT_PROJECT_VERSION`（build 号）**同一版本号下必须递增**，否则上传被拒
- `MARKETING_VERSION` 在 `project.pbxproj` 里共 **4 处**（主 App Debug/Release + Widget Debug/Release），
  必须一起改

```bash
grep -c "MARKETING_VERSION = 0.2.18;" MoonSalary.xcodeproj/project.pbxproj   # 应为 4
```

## 2. 构建环境（三个必设项）

```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
```

| 必设项 | 漏了会怎样 |
|---|---|
| `-derivedDataPath /tmp/...` | 工程在 iCloud Drive 下，actool 写 ICNS / Assets.car 会失败 |
| `OTHER_SWIFT_FLAGS='$(inherited) -Xfrontend -disable-sandbox'` | `swift-plugin-server` 起不来 → 满屏 `external macro implementation type 'SwiftUIMacros.StateMacro' could not be found`，且报错遍布未改动的文件 |
| `DEVELOPER_DIR` 指向 Xcode.app | `xcodebuild` / `devicectl` 都不可用 |

`$(inherited)` 不能省——CLI 传 `OTHER_SWIFT_FLAGS` 会**整体覆盖**工程里的设置。

## 3. 归档

### iOS

```bash
cd "<repo>"
xcodebuild archive \
  -project MoonSalary.xcodeproj \
  -scheme MoonSalary \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -archivePath /tmp/ms-archive/MoonSalary.xcarchive \
  -derivedDataPath /tmp/ms-archive-dd \
  -allowProvisioningUpdates \
  OTHER_SWIFT_FLAGS='$(inherited) -Xfrontend -disable-sandbox'
```

### macOS

```bash
xcodebuild archive \
  -project MoonSalary.xcodeproj \
  -scheme MoonSalary \
  -configuration Release \
  -destination 'generic/platform=macOS' \
  -archivePath /tmp/ms-archive-mac/MoonSalary.xcarchive \
  -derivedDataPath /tmp/ms-archive-mac-dd \
  -allowProvisioningUpdates \
  OTHER_SWIFT_FLAGS='$(inherited) -Xfrontend -disable-sandbox'
```

归档成功会打印 `** ARCHIVE SUCCEEDED **`。

> ⚠️ **`-allowProvisioningUpdates` 会重写 `project.pbxproj`。**
> 它会做一遍 Xcode 规范化（条目排序、缩进、补 `name`/`path`、
> `platformFilters` → `platformFilter`）。提交前先 `git diff` 看清楚，
> 别把无关改动混进功能提交。

## 4. 导出

`ExportOptions.plist`（`destination` 先写 `export`，确认没问题再改成 `upload`）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store-connect</string>
    <key>teamID</key>
    <string>3CKSH29X7T</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>uploadSymbols</key>
    <true/>
    <key>destination</key>
    <string>export</string>
    <key>manageAppVersionAndBuildNumber</key>
    <true/>
</dict>
</plist>
```

```bash
xcodebuild -exportArchive \
  -archivePath /tmp/ms-archive/MoonSalary.xcarchive \
  -exportPath /tmp/ms-archive/export \
  -exportOptionsPlist /tmp/ms-archive/ExportOptions.plist \
  -allowProvisioningUpdates
```

导出 iOS 得到 `<App>.ipa`，macOS 得到 `<App>.pkg`。

**导出是重新签名**，所以第 3 步归档出来是开发签名也没关系，不用重新构建。

## 5. 上传

把 `ExportOptions.plist` 里的 `destination` 从 `export` 改成 `upload`，重跑第 4 步，
即可直接上传到 App Store Connect。或者用 Xcode 的 Organizer（Window → Organizer）
手动 Distribute App。

上传后到 App Store Connect →「TestFlight」等构建处理完成（通常几分钟到半小时），
处理完才能提交审核。

## 6. 上传前自查

```bash
# 版本号
plutil -extract CFBundleShortVersionString raw -o - "<App>.app/Info.plist"

# 出口合规（应为 false）
plutil -extract ITSAppUsesNonExemptEncryption raw -o - "<App>.app/Info.plist"

# 隐私清单
ls "<App>.app/PrivacyInfo.xcprivacy"

# 扩展嵌入（iOS 应有、macOS 应无）
ls "<iOS App>.app/PlugIns"
ls "<macOS App>.app/Contents/PlugIns"

# 签名
codesign -dv --verbose=2 "<App>.app"
```

## 7. 常见报错对照

| 报错 | 原因 | 处理 |
|---|---|---|
| `error: exportArchive No Accounts` | Xcode 没登录 Apple ID，也没有 API Key | 登录 Xcode 账号，或改用 API Key 三参数（见 `docs/app-store-connect-api-key.md`） |
| `No profiles for 'xxx' were found ... iOS App Store provisioning profiles` | 没有分发证书 / App Store 描述文件 | 同上；登录后 Xcode 会自动创建 |
| `No signing certificate "iOS Distribution" found` | 同上 | 同上 |
| 满屏 `SwiftUIMacros.StateMacro could not be found` + `swift-plugin-server produced malformed response` | 宏插件子进程的沙箱无法嵌套 | 加 `OTHER_SWIFT_FLAGS='$(inherited) -Xfrontend -disable-sandbox'` |
| `actool ... ICNS` / Assets.car 失败 | DerivedData 落在 iCloud Drive | 改 `-derivedDataPath /tmp/...` |
| `error: 'accessoryInline' is unavailable in macOS` | 锁屏 accessory 系列是 iOS 专属 | `#if os(macOS)` 里返回合法 family |
| 上传后收到 ITMS-91053 | 缺少隐私清单或 required-reason API 声明 | 补 `PrivacyInfo.xcprivacy` |

## 8. 回滚

每次发布前后打 tag 作为安全网，命名沿用 `baseline/<版本>-<说明>`：

```bash
git tag -f baseline/0.2.18-asc-ready
```

已上传到 App Store Connect 的构建版本**无法删除**（只能从销售中移除），
所以上传前务必用 `git tag` 留好存档点。
