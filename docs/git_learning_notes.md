# Git / GitHub 学习调研笔记

调研日期：2026-10-27。已通过网页检索核对下列视频的标题、简介或章节信息，并用 Git / GitHub 官方文档核对操作方法。这里记录的是资料调研与操作指南，不把检索简介写成已完整观看视频，也不把操作步骤写成已完成的账户操作。

## 1. 视频学习资料

| 资料 | 类型 | 学习重点 |
| --- | --- | --- |
| [技术爬爬虾：Git+Github核心概念大串讲，从零到一全攻略，详细实战教程](https://www.youtube.com/watch?v=bWUUHBVg-7E) | 中文视频，2026-05-18 | 根据视频章节，可依次学习提交、分支、工作区与暂存区、远程仓库及协作。08:29 提交，14:17 分支，20:51 Git 分区，23:25 远程仓库，32:29 协作。 |
| [Darsh Patel：Getting Started with GitHub Desktop](https://www.youtube.com/watch?v=onBXXDzdLUw) | 英文桌面端入门视频，2024-11-05 | 根据视频简介与章节，学习创建仓库、push / pull、历史记录、暂存修改与冲突处理。0:57 创建仓库，1:47 推送，2:23 拉取，3:27 解决冲突。 |

建议观看顺序：先理解 Git 的提交和分支，再跟做 Desktop 的创建、提交、发布与同步。视频界面可能随版本变化；按钮含义以官方文档为准。

## 2. Git 的核心概念与命令

文件修改先发生在工作区；`git add` 把准备提交的内容放入暂存区；`git commit` 保存本地提交。修改已经暂存的文件后，如要包含新修改，需要再次 `git add`。提交不会自动上传 GitHub。[Git 官方教程：记录更新](https://git-scm.com/book/zh/v2/Git-基础-记录每次更新到仓库)

| 目的 | 常用命令 |
| --- | --- |
| 初始化 / 克隆 | `git init -b main` / `git clone 仓库地址` |
| 查看修改与提交 | `git status`、`git diff`、`git diff --cached`、`git log --oneline` |
| 暂存并提交 | `git add .`、`git commit -m "说明本次修改"` |
| 创建并切换功能分支 | `git switch -c feature/example` |
| 切回主分支 | `git switch main` |
| 查看远程仓库 | `git remote -v` |
| 首次关联远程仓库 | `git remote add origin 仓库地址` |
| 首次推送并设置上游 | `git push -u origin main` |
| 后续推送 | `git push` |
| 获取并仅快进更新 | `git pull --ff-only` |

`git switch -c` 创建并切换分支；`git push -u` 推送并建立上游跟踪关系。`git pull --ff-only` 获取远程修改，但只在能够快进时更新；本地与远程分叉时会停止，需先检查历史并选择合并或变基。[git-switch](https://git-scm.com/docs/git-switch)、[git-push](https://git-scm.com/docs/git-push)、[git-pull](https://git-scm.com/docs/git-pull)

协作时可在功能分支完成修改、测试并推送，然后发起 Pull Request，让合并前的讨论与审查有记录。[GitHub 官方：拉取请求](https://docs.github.com/zh/pull-requests/reference/pull-requests)

如果合并冲突，先用 `git status` 找到文件，编辑并确定最终内容，删除冲突标记，再测试、`git add 文件` 并提交。不能仅凭“保留当前”或“保留传入”盲选。[GitHub 官方：使用命令行解决合并冲突](https://docs.github.com/zh/pull-requests/how-tos/merge-and-close-pull-requests/resolving-a-merge-conflict-using-the-command-line)

## 3. GitHub Desktop 发布本项目

1. 安装 GitHub Desktop，在 Windows 的 `File → Options → Accounts` 中登录自己的 GitHub 账户。[官方设置指南](https://docs.github.com/en/desktop/overview/getting-started-with-github-desktop)
2. 本项目已有本地 Git 仓库时，选择 `File → Add local repository`，选中项目根目录。若是普通文件夹，则按提示先创建仓库。
3. 在 `Changes` 查看差异，选择要提交的文件，填写 Summary，点击 `Commit to main`。`History` 用于查看提交记录。
4. 首次发布点击 `Publish repository`，填写仓库名和说明，并**取消勾选 `Keep this code private`**，以满足 Public 要求，再发布。发布后的修改通过 `Push origin` 上传。[官方：发布现有项目](https://docs.github.com/zh/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop)、[官方：创建第一个仓库](https://docs.github.com/zh/desktop/overview/creating-your-first-repository-using-github-desktop)
5. 后续工作先查看 `Fetch origin` 是否发现远程更新，按需 `Pull origin`；编辑、测试、Commit，再 `Push origin`。最后在 GitHub 网站核对可见性为 Public、文件齐全以及 README 可读。

## 4. 本项目的管理约定

- 保留源码、接口、launch、YAML、说明与验证脚本；通过 `.gitignore` 排除 ROS2 的 `build/`、`install/`、`log/` 和 Python 缓存。
- 配置和安装资源使用项目相对路径或 ROS2 包的 share 目录，避免写入个人电脑的绝对路径。
- README 记录依赖、命令、期望输出、验证状态与现有限制；提交信息描述具体改动。
- 发布完成后从新目录克隆，按 README 重建运行，用这一过程检查遗漏文件和路径依赖。
