#!/usr/bin/env bash
set -eo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v ros2 >/dev/null 2>&1; then
    source "/opt/ros/${ROS_DISTRO:-jazzy}/setup.bash"
fi
workspace_setup="$project_root/exam2/ros2_ws/install/setup.bash"
if [[ ! -f "$workspace_setup" ]]; then
    echo "Build first: bash scripts/build_ros2.sh" >&2
    exit 1
fi
source "$workspace_setup"
exec ros2 launch robot_nodes robot_system.launch.py "$@"
