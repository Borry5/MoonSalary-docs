# 月薪鸭 · 官方文档

本仓库是 **月薪鸭（MoonSalary）** 的官方文档仓库，同时通过 GitHub Pages 提供 App Store 上架所需的隐私政策与技术支持页面。

- 站点地址：<https://borry5.github.io/MoonSalary-docs/>
- 隐私政策：<https://borry5.github.io/MoonSalary-docs/privacy/>
- 技术支持：<https://borry5.github.io/MoonSalary-docs/support/>

## 目录

| 路径 | 内容 |
|---|---|
| `index.html` | 产品主页（功能介绍 + 导航） |
| `privacy/` | 隐私政策（中文 + English） |
| `support/` | 技术支持、常见问题、联系方式 |
| `app-store/` | App Store 上架资料：文案、隐私问卷、年龄分级、审核备注、截图成品 |
| `docs/architecture.md` | 技术架构、工程结构、平台限制、已冻结功能表 |
| `docs/release-process.md` | 打包 → 签名 → 上传的完整链路 + 常见报错对照 |
| `docs/compliance.md` | 上架合规清单、已识别风险、提交前待办 |
| `docs/app-store-screenshots.md` | 截图尺寸要求与生成流程（模拟器播种 / macOS 离屏渲染） |
| `docs/app-store-connect-api-key.md` | 在 Xcode 登录 Apple ID / 生成 API Key 的图文步骤 |

## 关于月薪鸭

一款给打工人用的「实时进账」App。把月薪换算成看得见的每秒收入，在 iPhone 锁屏和 Mac 菜单栏上实时滚动。

- **iOS**：锁屏小组件（矩形 + 行内两种），**仅 iPhone**（0.2.18 起取消 iPad 支持）
- **macOS**：菜单栏常驻实时显示
- **工作日口径**：双休（含调休）／大小周／单休，双休方案自动跟随中国大陆法定节假日与调休
- **薪资口径**：按月 / 按日 / 按时三档联动，日薪为真值
- **数据**：全部本地存储，跨设备走你自己的 iCloud 私有空间

## 当前版本

**0.2.18**（构建号 1）——对应发布分支 `release` 的 tag `baseline/0.2.18-asc-ready`。

> ⚠️ 打包上传的硬阻塞：本机 Xcode 尚未登录 Apple ID，
> 只有 `Apple Development` 证书、没有 `Apple Distribution`。
> 解决步骤见 [`docs/app-store-connect-api-key.md`](docs/app-store-connect-api-key.md)。

## 维护说明

本仓库的页面是纯静态 HTML，不依赖构建工具。修改后直接提交到 `main` 分支，GitHub Pages 会自动重新发布（通常 1 分钟内生效）。

App Store 上架资料的文案部分（`app-store/metadata.md`）在每次发版时同步更新。
