#!/usr/bin/env bash
# Resolve the workspace from this script, so moving/cloning the project is safe.
set -eo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v ros2 >/dev/null 2>&1; then
    ros_setup="/opt/ros/${ROS_DISTRO:-jazzy}/setup.bash"
    if [[ ! -f "$ros_setup" ]]; then
        echo "ROS2 is missing. Install ROS2 Jazzy or source your ROS2 environment first." >&2
        exit 1
    fi
    source "$ros_setup"
fi
if ! command -v colcon >/dev/null 2>&1; then
    echo "colcon is missing. Install python3-colcon-common-extensions." >&2
    exit 1
fi
cd "$project_root/exam2/ros2_ws"
colcon build --symlink-install --event-handlers console_direct+
source install/setup.bash
if [[ "${1:-}" == "--verify" ]]; then
    python3 "$project_root/scripts/verify_ros2.py"
fi
