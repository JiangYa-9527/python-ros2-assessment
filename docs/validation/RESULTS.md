# 本次验证记录

记录日期：2026-10-27。此文件区分实际执行结果与待完成步骤，不将预期输出作为测试结果。

## 已执行

- Windows 环境使用 Python 3.12 运行 `python -B -m unittest discover -s tests -v`：20 项全部通过。
- 测试包含成绩、Book 和字符统计的真实子进程输入输出，以及 ROS2 接口、依赖、入口点、资源和配置静态检查。
- 两个 Bash 构建/启动脚本通过 `bash -n` 语法检查。
- ZIP 完整性检查通过，`exam1/` 中恰好三份源码，缓存和生成元数据已排除。
- ZIP 解压到 Windows 含空格的新目录后，全部 20 项测试通过，详见 [ZIP 可移植性记录](zip_portability.txt)。
- Git 本地仓库已初始化，主分支为 `main`。

## ROS2 实测结果

环境：WSL Ubuntu 24.04、ROS2 Jazzy、Python 3.12.3、GCC 13.3。全部测试使用实际 ROS2 节点和 CLI，没有用模拟 rclpy 代替通信。

| 检查 | 结果 | 日志 |
| --- | --- | --- |
| 实际 colcon build | 2 个包构建成功，用时 46.7 秒 | [构建](ros2_build.txt) |
| 默认 launch | 四节点、消息/服务类型、消息字段、sum=8、YAML 参数、订阅/客户端日志均通过；实测 1.000 Hz | [默认运行](ros2_default.txt) |
| ns=robot2、node_name=renamed_publisher | 使用修正后的验证器复测，四节点与通信、参数加载全部通过；实测 1.000 Hz | [改名运行](ros2_override.txt) |
| 四个程序独立 ros2 run | 订阅回调收到消息；一次性客户端及 CLI 调用均返回 8；topic hz 为 1.000 Hz | [独立运行](ros2_standalone.txt) |
| 迁移到含空格的新目录，重新构建 | 2 个包从干净目录构建成功；12 项基础题测试通过；全部通信验收通过，实测 1.000 Hz | [迁移重建](ros2_relocated.txt) |

迁移测试首次遇到 CLI 守护进程发现节点的短暂延迟。验证器已改为参数查询直接发现、显式等待并对 `Node not found` 有限重试，随后默认场景和迁移场景均通过。迁移日志保留首次失败及修复后成功记录。测试结束后已停止测试节点；本地构建输出和缓存由 Git/打包规则排除。

## 远程仓库回读

从 Public 仓库全新克隆提交 `a96bb50ce82e698450b8d28cd3c8f72030a6f202` 到含空格的新 Linux 路径，确认 38 个跟踪文件。20 项测试全部通过；两个 ROS2 包从零构建成功，用时 11.1 秒；实际消息、服务、YAML 和四节点通信验证通过，实测 1.000 Hz。没有复用原项目源码、构建目录或 overlay。

首轮 [GitHub Actions](https://github.com/JiangYa-9527/python-ros2-assessment/actions/runs/40533353201) 的 Python、构建和默认通信通过，改名场景出现 DDS 端点发现延迟：发布/订阅/服务日志正常，但一次性的 CLI 话题列表尚未发现目标。验证脚本因此增加了话题和服务的直接发现等待与有限重试，仍要求收到真实消息及正确的服务结果；后续远程结果见 [Actions 页面](https://github.com/JiangYa-9527/python-ros2-assessment/actions)。

## GitHub 发布状态

用户完成浏览器登录后，已创建 [JiangYa-9527/python-ros2-assessment](https://github.com/JiangYa-9527/python-ros2-assessment)，并通过 GitHub 元数据确认 `visibility=public`。连接器写入返回 403，改用已登录的 GitHub 网页按原目录提交源码和验证记录。GitHub Actions 已配置；远程结果须以该仓库 Actions 页面为准，本记录中的通过结果均来自本地实际执行。
