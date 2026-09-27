# Windows 安装与恢复（待实机验证）

本包包含统一 JavaScript 汉化源码、Windows 专用词条及 Python 安装器，不是已签名的 EXE 安装程序。**尚未在 Windows GitHub Desktop 实机完成验收。**

1. 安装 Python 3.9+ 和官方 GitHub Desktop。确认实际版本为 3.6.6。
2. 在任务管理器中查看 GitHub Desktop 的实际程序路径。资源目录通常是 `%LOCALAPPDATA%\GitHubDesktop\app-3.6.6\resources\app`，但必须按本机路径核对；不能仅按文件夹名猜当前版本。
3. 完全退出 GitHub Desktop。解压本包，在目录中打开 PowerShell。下载源码而非构建包时，先执行 `py -3 build.py`。
4. 替换下面 `$app` 的值为核对过的路径：

```powershell
$app = "$env:LOCALAPPDATA\GitHubDesktop\app-3.6.6\resources\app"
$backup = "$env:USERPROFILE\GitHubDesktop-zh-backup-0.3.0"
py -3 install.py check --app-dir "$app"
```

只读检查通过后执行：

```powershell
py -3 install.py install --app-dir "$app" --backup-dir "$backup"
```

备份目录必须尚不存在。按用户安装的 GitHub Desktop 通常不需要管理员权限。不要给全部用户开放目录权限。若本机只有 `app.asar`、不同版本或未知入口，脚本会拒绝安装，需要单独适配；不要绕过完整性检查。

## 验收

检查菜单、右键操作、设置、分支弹窗、中文数量与时间。确认代码、路径、仓库名、分支名和提交消息未被翻译，按钮和快捷键仍正常工作。退出后再次打开验证。验收时不要对真实仓库执行删除、提交或推送等操作。详细适配参考 [Windows 开发交接说明](windows-adaptation.md)。

## 恢复

退出应用，在同一个 PowerShell 中执行：

```powershell
py -3 install.py restore --app-dir "$app" --backup-dir "$backup"
```

会核对当前补丁和备份的 SHA-256。自动更新或其他改动后拒绝用旧备份覆盖；重新核对版本后适配。保留备份，不要上传它；它含本机应用路径和原文件。
