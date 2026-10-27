# Python / ROS2 综合考核项目

本项目使用 **Python** 完成考核一和考核二；考核三的 Git / GitHub 学习研究报告也收录在本文中。源码不依赖个人电脑的固定路径，克隆或解压后可按下列步骤构建。

## 1. 文件结构和考核对应关系

```text
exam1/                                  # 考核一：三份独立源码
  question1_scores.py                    # 10 人成绩降序排序
  question2_book.py                      # Book 类
  question3_char_count.py                # 字符分类统计
exam2/ros2_ws/src/
  robot_interfaces/                     # ament_cmake 自定义接口包
    msg/RobotStatus.msg
    srv/AddTwoInts.srv
    CMakeLists.txt
    package.xml
  robot_nodes/                          # ament_python 节点包
    robot_nodes/                        # 四个节点及公共清理函数
    launch/robot_system.launch.py
    config/params.yaml
    resource/robot_nodes
    setup.py / setup.cfg / package.xml
scripts/
  build_ros2.sh                         # 按脚本位置定位工作空间并构建
  run_ros2.sh                           # 启动四节点，可转发 launch 参数
  verify_ros2.py                        # 真正使用 ROS2 CLI 的通信验收
  package_submission.py                 # 生成干净的提交 ZIP
tests/                                  # Python 功能测试和项目静态检查
docs/git_learning_notes.md              # Git 学习调研扩展笔记
.github/workflows/check.yml             # GitHub Actions 自动构建及通信检查
```

## 2. 考核一：Python 代码能力

依赖 Python 3.10 或更高版本，无第三方库。以下命令在项目根目录执行；Windows 可将 `python3` 换成 `python`。

### 第一题：成绩降序排序

```bash
python3 exam1/question1_scores.py
```

输入恰好 10 个整数，支持空格、逗号或分行输入：

```text
78 92 65 88 70 95 82 60 100 85
```

输出：

```text
100 95 92 88 85 82 78 70 65 60
```

实现使用 `sorted(scores, reverse=True)`，返回降序新列表；数量不符或出现非整数会提示输入错误。

### 第二题：Book 类

```bash
python3 exam1/question2_book.py
```

输入：

```text
C++入门
45.5
20
```

输出：

```text
书名：C++入门
价格：45.5
库存：20
```

`Book` 通过 `__init__()` 初始化 `__title`、`__price`、`__stock`，通过 `input_data()` 读入、`display_data()` 输出。Python 的双下划线触发名称改写；实例生命周期由 Python 管理，无需 C++ 的 `new/delete`。

### 第三题：字符统计

```bash
python3 exam1/question3_char_count.py
```

输入 `AbC123 !中文`，输出：

```text
英文字母个数：3
数字个数：3
其他字符个数：4
```

这里的英文字母为 `A-Z/a-z`，数字为 `0-9`。空格、标点、中文、全角数字等均算其他字符；输入结束的换行不计数，字符串中的空格保留。逐个判断字符，时间复杂度为 O(n)。

## 3. 考核二：ROS2 环境与编译

目标环境为 **Ubuntu 24.04 + ROS2 Jazzy + Python 3.12**，可使用原生 Ubuntu 或 Windows 的 Ubuntu WSL。基础题可在 Windows 直接运行；下列 ROS2 命令在 Ubuntu Bash 中执行。

首先按 [ROS2 Jazzy 官方 Ubuntu 安装说明](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)安装 ROS Base 和开发工具。ROS2 自定义接口须通过 `ament_cmake` 生成，即使使用接口的节点是 Python，也应保留独立接口包。[自定义接口官方教程](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html)

在已配置 ROS2 软件源的系统中安装依赖：

```bash
sudo apt update
sudo apt install ros-jazzy-ros-base python3-colcon-common-extensions python3-rosdep python3-yaml
source /opt/ros/jazzy/setup.bash
```

进入克隆或解压后的项目根目录，执行：

```bash
# 首次使用 rosdep 时执行一次；已经初始化时跳过 init。
sudo rosdep init
rosdep update
rosdep install --from-paths exam2/ros2_ws/src --ignore-src --rosdistro jazzy -r -y

bash scripts/build_ros2.sh
source exam2/ros2_ws/install/setup.bash
```

构建脚本等价于在 `exam2/ros2_ws` 内执行 `colcon build --symlink-install`。`robot_interfaces` 的消息和服务生成完成后，`robot_nodes` 才能导入它们。每个新终端都要加载 ROS2 环境和工作空间的 `install/setup.bash`。

### 第一题：自定义话题

`RobotStatus.msg`：

```text
string robot_name
float32 speed
float32 position_x
float32 position_y
```

打开两个已加载环境的终端，分别执行：

```bash
ros2 run robot_nodes robot_status_publisher
```

```bash
ros2 run robot_nodes robot_status_subscriber
```

独立启动时，发布者以 **1 Hz** 在 `/robot_status` 上发布消息；订阅者在回调中输出名称、速度及坐标。示例名称是 `robot_demo`，速度为 `0.5`，坐标随发布次数改变。另开终端检查：

```bash
ros2 interface show robot_interfaces/msg/RobotStatus
ros2 topic list -t
ros2 topic echo /robot_status --once
ros2 topic hz /robot_status
```

`topic hz` 的测量值可能受启动发现、系统调度影响，持续观察应接近 1 Hz，按 Ctrl+C 停止。

### 第二题：自定义服务

`AddTwoInts.srv`：

```text
int64 a
int64 b
---
int64 sum
```

先启动服务端：

```bash
ros2 run robot_nodes add_two_ints_server
```

另一个终端启动客户端，默认发送 `a=3, b=5`，收到结果后输出 `Result: 3 + 5 = 8` 并退出：

```bash
ros2 run robot_nodes add_two_ints_client
ros2 service list -t
ros2 service call /add_two_ints robot_interfaces/srv/AddTwoInts "{a: 3, b: 5}"
```

手动调用的响应应包含 `sum=8`。也可以设置其他操作数：

```bash
ros2 run robot_nodes add_two_ints_client --ros-args -p a:=12 -p b:=30
```

请求字段和结果均须在 int64 范围内；接口没有错误响应字段，本练习不接受相加后溢出的输入。

### 第三题：launch、重命名、命名空间和 YAML

先用 Ctrl+C 停止上述独立运行节点，再一键启动：

```bash
bash scripts/run_ros2.sh
# 等价于：ros2 launch robot_nodes robot_system.launch.py
```

四个可执行程序保持题目指定的名称，所有节点 `output="screen"`。题目同时要求四种节点名称和 `atil_1` 重命名，本实现将**发布者**重命名为 `atil_1`，其他三个节点保留原名。没有把四个节点全部改为同名，以保证可以分别发现和管理。

| 可执行程序 | 一键启动后的节点名 | YAML 顶层键 |
| --- | --- | --- |
| robot_status_publisher | /robot1/atil_1 | atil_1 |
| robot_status_subscriber | /robot1/robot_status_subscriber | robot_status_subscriber |
| add_two_ints_server | /robot1/add_two_ints_server | add_two_ints_server |
| add_two_ints_client | /robot1/add_two_ints_client | add_two_ints_client |

`node_name` 是本 launch 声明的参数；现代 `launch_ros.actions.Node` 使用 `name=...` 设置运行时名字，因此代码将该参数传给 `Node(name=...)`。命名空间由 `ns` 参数传入 `Node(namespace=...)`。

`config/params.yaml` 的核心配置如下；完整文件还含客户端操作数和重复调用选项：

```yaml
atil_1:
  ros__parameters:
    publish_frequency: 1.0
    topic_name: robot_status
robot_status_subscriber:
  ros__parameters:
    topic_name: robot_status
add_two_ints_server:
  ros__parameters:
    service_name: add_two_ints
add_two_ints_client:
  ros__parameters:
    service_name: add_two_ints
    repeat: true
```

节点使用 `declare_parameter()` 声明，再用 `get_parameter()` 读取。launch 从包安装后的 share 目录找到 YAML，读取各节点的 `ros__parameters` 字典并通过 `parameters=[...]` 传入。这样修改命名空间或发布者名称后，参数仍能加载；默认 YAML 键与默认运行节点名一致。自定义配置文件沿用这些配置键。更多背景见 [ROS2 参数与 launch 官方教程](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Using-ROS2-Launch-For-Large-Projects.html)。

YAML 中的话题和服务名是相对名称，因此在 `robot1` 内解析为 `/robot1/robot_status` 和 `/robot1/add_two_ints`。单独 `ros2 run` 时的代码默认值带 `/`，保持前两题要求的全局名称。客户端 YAML 设置 `repeat: true`，每 2 秒调用一次，使四个节点在验收时持续存在；异步检查服务就绪状态，可适应服务端启动先后顺序。

另一个已加载环境的终端执行：

```bash
ros2 node list
ros2 topic list -t
ros2 service list -t
ros2 topic echo /robot1/robot_status --once
ros2 service call /robot1/add_two_ints robot_interfaces/srv/AddTwoInts "{a: 3, b: 5}"
ros2 param get /robot1/atil_1 publish_frequency
ros2 param get /robot1/robot_status_subscriber topic_name
ros2 param get /robot1/add_two_ints_server service_name
ros2 param get /robot1/add_two_ints_client service_name
```

节点列表应包含上表的四个节点，频率参数为 `1.0`，服务响应包含 `sum=8`。`topic list` 还可能包含 `/rosout`、`/parameter_events`，`service list` 也会包含节点参数服务，属于正常情况。

可在任意目录通过脚本完整路径启动，或在项目根目录修改名称：

```bash
bash scripts/run_ros2.sh ns:=robot2 node_name:=renamed_publisher
# 使用自定义 YAML 时，参数文件路径改为自己的实际路径：
# bash scripts/run_ros2.sh params_file:=/absolute/path/to/params.yaml
```

这时发布者为 `/robot2/renamed_publisher`，话题和服务也相应进入 `/robot2`。

## 4. 验证、可移植性与提交

无需 ROS2 的测试：

```bash
python3 -B -m unittest discover -s tests -v
```

该测试包含基础题真实输入输出、边界情况，以及接口、包依赖、入口、语法和资源检查；**静态检查不代表 ROS2 通信验证通过**。

已构建并加载 ROS2 环境后，执行实际验收：

```bash
python3 scripts/verify_ros2.py
python3 scripts/verify_ros2.py --ns robot2 --node-name renamed_publisher
# 或从构建开始：
bash scripts/build_ros2.sh --verify
```

验证脚本启动真正的四节点 launch，检查节点发现、自定义话题和服务类型、消息字段、`sum=8`、发布频率参数、订阅与客户端日志，并在结束时清理自己启动的进程。默认选择一个 ROS domain，已有 `ROS_DOMAIN_ID` 时沿用；请避免在同一 domain 同时运行其他同名演示。GitHub Actions 也已配置基础测试、ROS2 构建和两组通信验收，只有远程实际运行成功才可认定 CI 通过。

验证状态详见 [本次验证记录](docs/validation/RESULTS.md)。代码不含个人项目绝对路径；移动或重新克隆后须重新构建，不能沿用旧路径的 `build/install/log`。`.gitignore` 和 ZIP 打包脚本排除这些产物及 Python 缓存。

生成提交包：

```bash
python3 scripts/package_submission.py
```

输出 `dist/python-ros2-assessment.zip`，其中 `exam1` 目录保存题目要求的三份源码。压缩包包含 ROS2 源码、配置、说明和验证脚本。

## 5. 考核三：Git / GitHub 学习研究报告

调研日期：2026-10-27。已联网检索学习视频，并核对视频标题、简介或章节及官方文档；此记录不表示已经完整观看视频或手动操作了 GitHub Desktop。

### 学习视频与资料

| 资料 | 建议学习内容 |
| --- | --- |
| [技术爬爬虾：Git+Github核心概念大串讲，从零到一全攻略](https://www.youtube.com/watch?v=bWUUHBVg-7E) | 中文视频：08:29 提交，14:17 分支，20:51 分区，23:25 远程仓库，32:29 协作。 |
| [Darsh Patel：Getting Started with GitHub Desktop](https://www.youtube.com/watch?v=onBXXDzdLUw) | 桌面端视频：0:57 创建，1:47 推送，2:23 拉取，3:27 处理冲突。 |
| [Git 官方中文书：记录更新](https://git-scm.com/book/zh/v2/Git-基础-记录每次更新到仓库) | 核对工作区、暂存区、本地提交。 |
| [GitHub Desktop 官方发布指南](https://docs.github.com/zh/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop) | 核对导入现有仓库、发布及 Public 设置。 |

### Git 命令的理解与使用

Git 管理版本历史，GitHub 托管远程仓库。编辑发生在工作区，`git add` 把本次要提交的修改加入暂存区，`git commit` 保存本地版本，`git push` 才会上传远程。再次修改已暂存文件后，需要重新暂存以包含新修改。[Git 官方说明](https://git-scm.com/book/zh/v2/Git-基础-记录每次更新到仓库)

| 操作 | 命令 |
| --- | --- |
| 初始化主分支 | `git init -b main` |
| 查看改动 / 已暂存改动 | `git status`、`git diff`、`git diff --cached` |
| 暂存与提交 | `git add .`、`git commit -m "Complete Python and ROS2 assessment"` |
| 查看历史 | `git log --oneline` |
| 创建功能分支 | `git switch -c feature/example` |
| 关联远程 | `git remote add origin 你的仓库地址` |
| 首次上传 | `git push -u origin main` |
| 后续同步 | `git pull --ff-only`、`git push` |
| 克隆验证 | `git clone 你的仓库地址` |

`pull --ff-only` 在历史分叉时停止，需查看历史后决定合并或变基。[git-pull 文档](https://git-scm.com/docs/git-pull) 团队协作应在功能分支提交、测试、推送，通过 Pull Request 讨论并合并；出现冲突时逐处确定正确内容，删除冲突标记、测试、暂存后提交。[GitHub 冲突处理文档](https://docs.github.com/zh/pull-requests/how-tos/merge-and-close-pull-requests/resolving-a-merge-conflict-using-the-command-line)

### GitHub Desktop 的实际操作流程

1. 登录自己的 GitHub 账号，选择 `File → Add local repository`，导入本项目根目录。本项目若已有 `.git`，无需重复创建。
2. 在 `Changes` 检查文件差异，填提交摘要，点击 `Commit to main`；通过 `History` 查看历史。
3. 尚无远程仓库时点击 `Publish repository`，填写名称，**取消 `Keep this code private` 勾选**，发布为 Public。已关联远程时使用 `Push origin`。[Public 设置官方依据](https://docs.github.com/zh/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop)
4. 后续修改前查看 `Fetch origin` 和 `Pull origin`，完成修改和测试后 Commit，再 Push。
5. 在 GitHub 网页确认 Public、README 和源码完整；从新目录克隆，重新构建和运行，检查是否遗漏文件或依赖个人路径。

本项目把源码、接口、配置、README 和检查脚本纳入版本管理；构建产物不提交。路径从脚本位置或包的 share 目录解析。这样在另一台同环境电脑上，只需选择自己的克隆目录、安装依赖并重新构建即可运行。完整调研见 [学习笔记](docs/git_learning_notes.md)；远程发布结果以验证记录为准。
