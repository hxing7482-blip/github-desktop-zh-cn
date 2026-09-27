# 请 Windows 端 Codex 适配并部署 GitHub Desktop 中文补丁

用户需求：把 GitHub Desktop 的功能选项、菜单、右键菜单、设置与弹窗汉化，尽可能覆盖当前安装版本。用户希望你实际完成部署与验收，不仅提供操作步骤。

本包是 Windows 适配源码交接包，不是已在 Windows 验证的安装器。基线为 Mac GitHub Desktop 3.6.6，补丁 0.2.2；包含 1,654 条静态词条及动态模板，补充了资源管理器、回收站、命令提示符等 Windows 文案。Mac 端仓库右键菜单已经实际验证为中文。0.2.2 修复了代码差异预览里 version/name 等标识符被误译的问题，已通过离线回归测试。

## 1. 检查本机，先备份

确认 Windows 本机的 GitHub Desktop 版本、安装目录、入口 package.json、Electron 资源布局。可以检查 %LOCALAPPDATA%\GitHubDesktop 下当前 app-* 目录，但必须结合正在运行的可执行文件路径确定实际使用的版本，不能直接猜路径。

退出 GitHub Desktop 并确认进程已结束。备份本机即将修改的文件及其 SHA-256，记录版本、路径和时间。备份放在应用目录以外。不需要修改用户登录配置、仓库、提交记录、分支、Git 配置或 Windows 安全设置。

如果版本不是 3.6.6，请先核对入口与 DOM/菜单结构，再适配；不要把本包当作任意版本都能直接覆盖的补丁。不要从 Mac 复制 main.js、renderer.js、index.html 或完整应用：本包故意不包含这些文件。

## 2. 构建或使用 build 目录

build/ 已包含构建好的 zh-core.js、zh-main.cjs、zh-renderer.js、zh-NOTICE.txt。
修改词条后，可在本包根目录执行：

    python build.py

构建仅依赖 Python 标准库。构建结果是平台无关的 JavaScript；保留 zh-NOTICE.txt 中的第三方词典许可。

## 3. 适配本机 Electron 入口

若本机使用未打包的 resources/app 目录：

1. 确認主入口；本基线为 main.js。将 build/ 的四个 zh-* 文件复制到适当的入口目录。
2. 在本机原始主入口最前面引入：

       require('./zh-main.cjs'); // desktop-local-zh v0.2.2

   如果本机入口不在此目录，调整相对路径。只添加一次；如果已有其他汉化补丁，先辨认，避免重复注入或破坏旧补丁。
3. 在本机 index.html 的原 renderer.js 脚本之后，按以下顺序加入：

       <script defer src="zh-core.js"></script>
       <script defer src="zh-renderer.js"></script>

   保留原来的其他标签、资源路径和安全配置。如果现有脚本加载方式或内容安全策略不同，结合本机文件适配，不要粗暴关闭安全策略。
4. 不修改 renderer.js 中的业务逻辑、菜单命令、函数名或 Git 操作。

若资源在 app.asar 中：先备份 app.asar 和相关 unpacked 目录。使用与本机 Electron 兼容的官方 @electron/asar 工具流程进行有针对性的处理，保留解包文件标记和完整性要求。如果应用的资源完整性校验阻止修改，报告具体情况，不要关闭系统防护或随意修改可执行文件来绕过。

## 4. 汉化实现与已知重点

- zh-main.cjs：拦截 Menu.buildFromTemplate、Menu.prototype.append/insert，以及原生对话框的显示文案。直接 append(new MenuItem(...)) 的右键菜单必须覆盖，只拦截模板是不够的。
- zh-renderer.js：原地改文本节点和 aria-label/title/placeholder。不能替换 React 元素，不能改输入 value、option value、按钮回调、命令 ID、checkbox 状态或用户内容。
- zh-core.js：静态词典、大小写/省略号/空白匹配及带变量的文案模板。
- Windows 有些菜单带 & 助记符，需检查本机实际效果；原生快捷键/accelerator 应保持原有行为。
- 3.6.6 的代码差异 DOM 使用 .side-by-side-diff .content（内部包含 .content-wrapper），必须排除。不能只排除 code/pre 或假设有 .diff 类，否则 version/name 等代码标识会被误译。
- 仓库名、分支名、标签名、提交摘要、评论正文、文件路径、代码与用户输入保留原文。若本机 DOM 类名不同，扩充排除规则并验证。
- 法律/开源许可正文、产品型号、服务端原始错误及项目本身的内容不属于功能选项汉化；不要声称已穷尽所有第三方英文内容。

## 5. 必须完成的验证

可先运行 node tests/native.cjs（只依赖 Node 标准库）。它测试菜单回调、ID、启用状态、原生弹窗按钮顺序与路径是否保持。

tests/ui.cjs 依赖 Playwright，可使用本机已有运行库；如已有 Chrome，可设置 CHROME_PATH 为本机可执行文件路径。没有 Chrome 时使用 Playwright 自带浏览器。该测试使用独立无登录的本地 HTML，验证按钮点击、输入值、option 值、动态更新，以及代码和用户文本不被翻译。

实机验收至少包括：
- 顶栏文件/编辑/查看/仓库/分支/帮助菜单。
- 仓库右键菜单：创建别名、显示工作树、新建工作树、复制名称/路径、在 GitHub 上查看、终端、资源管理器、外部编辑器、移除。
- 文件与提交右键菜单、提交选项、差异显示选项。
- 设置中的账户、Git、外观、集成、高级及本机存在的 Copilot 页面。
- 新建/克隆仓库与分支/工作树弹窗，仅打开查看后取消；不要为了验收创建、删除、提交或推送用户的真实仓库。
- 代码预览中的 version/name/Settings/History 必须保持英文代码本身；仓库与分支名字也不能误译。
- 关闭再打开至少一次，确认补丁继续生效且应用启动正常。

对发现的漏译补齐后再交付；报告实际检查过的页面和未覆盖边界，不把词条数量当作全部功能已验证的证据。

## 6. 回滚与后续更新

生成本机恢复脚本或包：恢复前对已安装补丁文件做 SHA-256 检查，与部署清单一致才恢复对应版本的原文件、删除本次新增的 zh-* 文件。遇到 GitHub Desktop 自动更新导致版本或哈希变化，应拒绝用旧备份覆盖新版本，并重新适配。不要关闭自动更新。

请交回：实际 Windows 版本/资源路径、安装时间、改动与备份清单、哈希、验收结果、回滚方式；不要返回账户凭据或令牌。

0.2.2 已修复分支菜单 Update from main 的模板匹配优先级，并保留代码行保护同时翻译 Expand Up/Down 按钮。新增回归测试已通过。
