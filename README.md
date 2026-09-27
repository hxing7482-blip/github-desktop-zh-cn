# GitHub Desktop 简体中文补丁

非官方、开源的 GitHub Desktop 界面汉化补丁，面向 **macOS 和 Windows**。汉化菜单、右键操作、设置、对话框与常见提示，保留代码、仓库名、分支名、文件路径及用户输入原文。

> 本项目不是 GitHub 官方产品，也不是 GitHub 官方支持的插件机制。它通过给本机 Electron 应用增加 JavaScript 文件实现翻译。GitHub Desktop 升级后可能覆盖补丁；不要把旧备份恢复到新版本上。

## 版本与验证范围

| 项目 | 状态 |
| --- | --- |
| 公开版本 | 0.3.0，基于已使用的 0.2.2 汉化代码整理 |
| 适配基线 | GitHub Desktop **3.6.6**，未封装的 `resources/app` 资源目录 |
| macOS | 0.2.2 核心在 Apple Silicon 实机验证过菜单、仓库右键、设置和代码差异；0.3.0 新安装器通过隔离目录的安装/恢复测试 |
| Windows | 提供统一源码、Windows 词条及安装/恢复命令；**尚未完成 Windows 实机验收** |
| 词条 | 1,654 条静态映射及动态规则；词条数量不等于穷尽所有运行界面 |

**先阅读 [Mac 安装说明](docs/macos.md) 或 [Windows 安装说明](docs/windows.md)。**

源码 ZIP 可从仓库的 Code → Download ZIP 下载；打包文件见 [下载目录](dist/)。两平台包均不含 GitHub Desktop 本体、用户账户数据或原应用备份。无需从本项目登录 GitHub，也不会采集登录令牌。

## 覆盖与边界

- 顶栏菜单、仓库/文件/提交右键菜单、分支与工作树操作、设置、原生弹窗、常见数量和时间提示。
- 原地替换文本节点及 `title`、`aria-label`、`placeholder`；不改按钮回调、命令 ID、输入值或 Git 业务逻辑。
- 排除代码差异、提交消息、仓库/分支名称等用户内容；已知 DOM 结构变化时需要重新验证排除规则。
- 不全文翻译第三方法律正文、服务器原始错误或用户项目内容。不承诺所有罕见界面都已汉化。
- 暂不自动修改 `app.asar`、不绕过应用完整性检查、不关闭系统安全设置或自动更新。
- 补丁会修改应用资源，可能影响 macOS 签名校验或受到系统权限保护。若系统阻止运行，恢复原版或从官方渠道重新安装，不要关闭 Gatekeeper 来规避。

## 构建与测试

构建只需要 Python 3.9+ 标准库；使用已构建包无需 Node.js。开发测试另需 Node.js 20+；UI 测试需 Playwright 与 Chromium/Chrome。

```sh
python3 build.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/native.cjs
npm ci
npx playwright install chromium
node tests/ui.cjs
```

Windows 将 `python3` 替换为 `py -3`。也可通过 `CHROME_PATH` 指定已有 Chrome 可执行文件。测试只使用合成 HTML 和临时应用目录，不操作你的真实仓库。

打包：`python3 scripts/package.py`，生成分别带 Mac/Windows 说明的源码与构建产物 ZIP、SHA-256 校验清单。旧的 0.2.2 `.pkg` 是针对上一版的本机升级包，不适合首次安装，因此不作为公开安装包分发。

## 贡献与许可

欢迎提交漏译的英文文本、对应中文、操作路径与版本号；截图请先遮盖账户、路径和项目内容。先复现并补充测试，再提交 Pull Request。参见 [贡献说明](CONTRIBUTING.md)。

本项目采用 [MIT License](LICENSE)。部分词典来源于 [twinightminer-arch/github-desktop-translate-to-chinese](https://github.com/twinightminer-arch/github-desktop-translate-to-chinese)，其版权及 MIT 许可完整保留于 [第三方许可](licenses/translation-dictionary-MIT.txt) 与 `src/zh-NOTICE.txt`。未再分发 GitHub Desktop 应用本体。GitHub 等商标归各自所有者所有。
