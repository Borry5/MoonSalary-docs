# App Store Connect API Key：是什么、要不要办、怎么办

## 一、先搞清楚：API Key 是不是必需品？

**不是。** 上传 App Store 有两条路，**任选一条即可**：

| 方案 | 需要什么 | 适合谁 |
|---|---|---|
| **A. 在 Xcode 里登录 Apple ID** | 你的 Apple ID + 密码（+ 双重验证） | ✅ **推荐给打表上班**，零成本、5 分钟 |
| **B. App Store Connect API Key** | 付费开发者账号的「用户和访问 → 集成」页面生成 `.p8` | 团队协作、CI 自动打包 |

打表上班现在卡在 `error: exportArchive No Accounts`，**根因是本机 Xcode 没登录任何 Apple ID**，
所以现在最省事的是**方案 A**。API Key 是给「不想在机器上存 Apple ID 密码」
或「想让脚本在服务器上无人值守上传」的场景用的。

> 两条路可以同时存在，不冲突。先走 A 把包传上去，将来要做 CI 再补 B 也不迟。

---

## 二、方案 A：在 Xcode 登录 Apple ID（推荐，先做这个）

1. 打开 **Xcode** → 菜单栏 **Xcode → Settings…**（快捷键 `⌘ ,`）
2. 切到 **Accounts** 标签页
3. 左下角点 **`+`** → 选 **Apple ID** → Continue
4. 输入你的 Apple ID 与密码，通过双重验证
5. 登录成功后，右侧会列出你的团队，确认能看到团队 **`3CKSH29X7T`**
6. 选中团队 → 点 **Manage Certificates…**
7. 左下角 **`+`** → 选 **Apple Distribution** → 证书会自动签发并装进钥匙串
8. 关掉窗口，回到终端验证：

```bash
security find-identity -v -p codesigning
```

输出里除了 `Apple Development: Bo Meng (...)`，**必须多出一行**
`Apple Distribution: ...`。有了它，导出与上传就通了。

**验证通过后直接跳到** `docs/release-process.md` 第 4 步重跑导出。

> 登录 Apple ID 会让 Xcode 自动创建 App Store 描述文件
> （`iOS App Store` 类型），所以第 0 节里「有 App Store 描述文件」那一项
> 不用你手动准备。

---

## 三、方案 B：生成 App Store Connect API Key

### 前提

- 你的账号必须是**付费的 Apple Developer Program 成员**（个人或组织均可）
- 账号角色必须是 **Account Holder / Admin / App Manager** 之一
  —— 只有这三类角色能看到「用户和访问」里的密钥页
  （Developer、Marketing、Finance 等角色看不到，会直接 403）

### 步骤

1. 浏览器打开 **<https://appstoreconnect.apple.com>**，用开发者账号登录
2. 进 **「用户和访问」**（Users and Access）
3. 顶部切到 **「集成」**（Integrations）标签页
   - 旧版界面叫 **「密钥」**（Keys）→ 再选 **App Store Connect API**
4. 左侧选 **「App Store Connect API」** → 点 **「团队密钥」**（Team Keys）区域的 **`+`**
5. 弹窗里填：
   - **名称**：随意，建议 `MoonSalary-Upload`（日后好辨认）
   - **访问权限**（Access）：**必须选 `App Manager`**
     - ❌ 别选 `Admin`：权限过大，Apple 自己也建议按需最小化
     - ❌ 别选 `Developer`：**传不了包**，`altool` / `notarytool` 会报权限不足
6. 点 **「生成」**（Generate）
7. **立刻下载 `.p8` 文件**（形如 `AuthKey_ABCDE12345.p8`）

> ⚠️ **`.p8` 只能下载一次。** 页面一刷新就再也拿不到了，
> 只能吊销后重新生成。下载后请立刻移到安全位置。

8. 回到密钥列表，记下这两个值（页面上随时可查，不怕丢）：

| 名称 | 长什么样 | 从哪看 |
|---|---|---|
| **Key ID** | 10 位大写字母数字，如 `ABCDE12345` | 密钥列表的「密钥 ID」列 |
| **Issuer ID** | UUID 形式，如 `69a6de70-03db-47e3-e053-5b8c7c11a4d1` | 页面顶部「Issuer ID」那一行，**全账号共用** |

### 三个值在命令里的对应关系

```bash
xcodebuild -exportArchive \
  -archivePath /tmp/ms-archive/MoonSalary.xcarchive \
  -exportPath /tmp/ms-archive/export \
  -exportOptionsPlist /tmp/ms-archive/ExportOptions.plist \
  -authenticationKeyPath   /path/to/AuthKey_ABCDE12345.p8 \
  -authenticationKeyID     ABCDE12345 \
  -authenticationKeyIssuerID 69a6de70-03db-47e3-e053-5b8c7c11a4d1
```

| 命令行参数 | 对应什么 |
|---|---|
| `-authenticationKeyPath` | 第 7 步下载的 `.p8` 文件路径 |
| `-authenticationKeyID` | 第 8 步的 **Key ID**（**不含** `AuthKey_` 前缀、**不含** `.p8` 后缀） |
| `-authenticationKeyIssuerID` | 第 8 步的 **Issuer ID** |

**三个参数必须同时给**，少一个会退回「找 Xcode 登录账号」的老路，继续报 `No Accounts`。

### 常见坑

| 现象 | 原因 |
|---|---|
| 密钥页里找不到「集成」/「App Store Connect API」 | 账号角色不够（需要 Account Holder / Admin / App Manager） |
| `Authentication credentials are missing or invalid` | Key ID 或 Issuer ID 抄错，或 `.p8` 路径不对 |
| 上传时 `The provided entity includes an attribute with an invalid value` | 访问权限选成了 `Developer`，重选 `App Manager` 重新生成 |
| `.p8` 找不到了 | 无法找回，只能吊销重生成（旧 Key 吊销后已上传的构建不受影响） |

---

## 四、安全提醒

- `.p8` 等同于账号的上传凭据，**不要提交进 Git**
- 本仓库 `.gitignore` 已挡住 `*.p8`，但仍建议把 `.p8` 放在仓库目录之外
- 只在需要时生成，用完可以在 App Store Connect 里**吊销**（Revoke）
- 千万不要把 `.p8`、Key ID、Issuer ID 贴到聊天记录或 issue 里

---

## 五、打表上班该选哪个？

**先用方案 A。** 理由：

1. 现在就卡在「没登录 Apple ID」，方案 A 是唯一的直接解
2. 单机开发，没有 CI，API Key 的收益（无人值守）用不上
3. 少一个需要保管的凭据文件

将来如果要接 GitHub Actions 自动打包上传，再回头看方案 B。
