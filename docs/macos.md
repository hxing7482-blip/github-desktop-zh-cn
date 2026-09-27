# macOS 安装与恢复

适配 GitHub Desktop 3.6.6、未封装的应用资源目录。先从官方渠道安装 GitHub Desktop，并确认原应用能正常启动。安装包中已带 `build/`；如果下载源码，先执行 `python3 build.py`。

完全退出 GitHub Desktop，在终端进入解压后的补丁目录，先执行只读检查：

```sh
python3 install.py check --app-dir '/Applications/GitHub Desktop.app/Contents/Resources/app'
```

检查通过后，安装并指定一个**尚不存在**的备份目录：

```sh
python3 install.py install --app-dir '/Applications/GitHub Desktop.app/Contents/Resources/app' --backup-dir "$HOME/GitHubDesktop-zh-backup-0.3.0"
```

如果提示没有应用目录写入权限，确认路径后给这一条安装命令加 `sudo`，在系统终端自行输入管理员密码。不要关闭系统保护。保留备份目录；它包含本机原始入口、路径和哈希，不要上传到公共仓库。

重新打开 GitHub Desktop，检查菜单、右键菜单、设置、代码差异和仓库/分支名称。再退出并打开一次检查持续生效。0.3.0 的新安装器目前通过的是隔离目录测试；此前实机验证的是 0.2.2 翻译核心。

## 恢复英文

退出应用，然后执行（如安装时用了 sudo，恢复时同样使用）：

```sh
python3 install.py restore --app-dir '/Applications/GitHub Desktop.app/Contents/Resources/app' --backup-dir "$HOME/GitHubDesktop-zh-backup-0.3.0"
```

恢复前验证全部补丁文件和原始备份哈希。应用已升级或文件被改动时会拒绝恢复，避免覆盖新版本。遇到这种情况，请从官方渠道重新安装对应应用，不要强制覆盖。

## 已安装旧版汉化的用户

此安装器拒绝叠加到旧补丁上。请使用旧版自己的匹配恢复包恢复英文，再执行检查和安装；没有匹配备份时，请先重新安装官方应用。此开源发布不会自动替换你当前能正常工作的旧汉化。
