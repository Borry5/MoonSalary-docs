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
| `app-store/` | App Store 上架资料：文案、隐私问卷、年龄分级、审核备注 |
| `docs/` | 技术文档：架构、发布流程、上架合规清单 |

## 关于月薪鸭

一款给打工人用的「实时进账」App。把月薪换算成看得见的每秒收入，在 iPhone 锁屏、主屏和 Mac 菜单栏上实时滚动。

- **iOS**：锁屏小组件（矩形 + 行内两种）
- **macOS**：菜单栏常驻实时显示
- **工作日口径**：双休（含调休）／大小周／单休，双休方案自动跟随中国大陆法定节假日与调休
- **薪资口径**：按月 / 按日 / 按时三档联动，日薪为真值
- **数据**：全部本地存储，跨设备走你自己的 iCloud 私有空间

## 维护说明

本仓库的页面是纯静态 HTML，不依赖构建工具。修改后直接提交到 `main` 分支，GitHub Pages 会自动重新发布（通常 1 分钟内生效）。

App Store 上架资料的文案部分（`app-store/metadata.md`）在每次发版时同步更新。
