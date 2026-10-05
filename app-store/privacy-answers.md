# App 隐私问卷答案（App Store Connect → App 隐私）

## 结论

在 App Store Connect 的「App 隐私」页面，选择：

```
否，我们不会从此 App 收集数据
```

选完之后问卷直接结束，不需要逐项勾选数据类型。

---

## 判断依据（逐条对照）

Apple 对「收集（collect）」的定义是：
**数据被传输离开设备，且开发者（或第三方合作伙伴）能够访问到它。**
仅仅在设备上处理、或者只存进用户自己的 iCloud 私有空间，都不算「收集」。

| 数据 | 实际去向 | 是否算收集 | 依据 |
|---|---|---|---|
| 薪资方案、工作日设置 | 本机 `UserDefaults` + App Group | 否 | 未离开设备 |
| 请假 / 加班记录 | 同上，开启同步后进用户自己的 iCloud KV | 否 | 存于用户 Apple ID 名下的私有空间，开发者无权访问 |
| 设备名录里的设备指纹 | 仅写入用户自己的 iCloud KV | 否 | 同上；SHA-256 哈希，不可逆，不上传开发者 |
| 网络请求携带的信息 | 只发送年份数字 | 否 | 不含任何用户或设备数据 |
| IP 地址 | 由 CDN 在技术层面可见 | 否 | 开发者不接收、不存储；这是网络通信固有属性，非本 App 主动采集 |

---

## 需要如实披露、但不属于「收集」的两处

这两项已写进隐私政策正文，建议审核被问到时按此口径答复。

### 1. 设备标识（Identifier）

- **iOS**：`UIDevice.current.identifierForVendor`（Apple 官方提供）
- **macOS**：`IOPlatformUUID`（主板平台 UUID）+ macOS 用户名 → SHA-256 哈希

用途：在 iCloud 的「设备名录」里区分「这是哪台设备」，让用户知道自己有几台设备在同步。

- 不用于广告
- 不用于跨 App 追踪
- 不上传开发者
- 不与第三方共享
- 只出现在用户自己的 iCloud 私有空间

对应隐私清单：`NSPrivacyTracking = false`，`NSPrivacyCollectedDataTypes` 为空数组。

### 2. 网络请求

- 请求 `cdn.jsdelivr.net` 与 `raw.githubusercontent.com` 上的公开节假日数据集
- 请求内容只有年份，无任何用户信息
- 无自建服务器，无埋点上报

---

## 隐私清单（PrivacyInfo.xcprivacy）实际内容

仓库内两份清单（主 App 与 Widget）内容一致：

```xml
<key>NSPrivacyTracking</key>            <false/>
<key>NSPrivacyTrackingDomains</key>     <array/>
<key>NSPrivacyCollectedDataTypes</key>  <array/>
<key>NSPrivacyAccessedAPITypes</key>
  <array>
    <dict>
      <key>NSPrivacyAccessedAPIType</key>
      <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
      <key>NSPrivacyAccessedAPITypeReasons</key>
      <array><string>CA92.1</string></array>
    </dict>
  </array>
```

**只有 `UserDefaults` 一项需要声明**（reason `CA92.1`：访问本 App 或 App Group 自己的用户偏好）。

已逐项排查并确认**未使用**以下 required-reason API：

- 文件时间戳（`fileModificationDate` / `attributesOfItem` / `contentModificationDateKey`）
- 系统启动时间（`systemUptime` / `mach_absolute_time`）
- 磁盘空间（`volumeAvailableCapacity` / `attributesOfFileSystem`）
- 活动键盘（`activeInputModes`）

---

## 出口合规（ITSAppUsesNonExemptEncryption）

已在 `project.pbxproj` 中为 app target 的 Debug / Release 均设置：

```
INFOPLIST_KEY_ITSAppUsesNonExemptEncryption = NO;
```

依据：

- `CryptoKit` 只用于 `SHA256.hash`（哈希，不是加密）
- 网络通信只用系统标准的 HTTPS / TLS
- 无自研或第三方加密算法
- 不含任何需要出口许可的加密功能

设置后，每次上传构建版本都不再需要在 App Store Connect 里手动回答加密问题。
