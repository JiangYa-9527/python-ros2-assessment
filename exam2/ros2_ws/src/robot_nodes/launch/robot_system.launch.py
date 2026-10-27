"""Launch four nodes, with YAML parameters, one namespace and a renamed publisher."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import yaml


def launch_nodes(context):
    namespace = LaunchConfiguration("ns").perform(context)
    publisher_name = LaunchConfiguration("node_name").perform(context)
    params_path = LaunchConfiguration("params_file").perform(context)
    with open(params_path, "r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ValueError("params_file must contain a mapping of node names")

    # Extract by the documented default names, then pass each parameter mapping
    # directly. A changed ns/node_name therefore does not invalidate YAML matching.
    specifications = [
        ("robot_status_publisher", publisher_name, "atil_1"),
        ("robot_status_subscriber", "robot_status_subscriber", "robot_status_subscriber"),
        ("add_two_ints_server", "add_two_ints_server", "add_two_ints_server"),
        ("add_two_ints_client", "add_two_ints_client", "add_two_ints_client"),
    ]
    nodes = []
    for executable, name, config_key in specifications:
        if config_key not in config or not isinstance(config[config_key], dict):
            raise ValueError(f"Missing YAML node configuration: {config_key}")
        parameters = config[config_key].get("ros__parameters")
        if not isinstance(parameters, dict):
            raise ValueError(f"Missing ros__parameters mapping for {config_key}")
        nodes.append(Node(
            package="robot_nodes",
            executable=executable,
            name=name,
            namespace=namespace,
            output="screen",
            parameters=[parameters],
        ))
    return nodes


def generate_launch_description():
    default_params = os.path.join(
        get_package_share_directory("robot_nodes"), "config", "params.yaml"
    )
    return LaunchDescription([
        DeclareLaunchArgument("ns", default_value="robot1", description="Shared namespace"),
        DeclareLaunchArgument(
            "node_name", default_value="atil_1", description="Publisher node name"
        ),
        DeclareLaunchArgument(
            "params_file", default_value=default_params, description="YAML configuration path"
        ),
        OpaqueFunction(function=launch_nodes),
    ])
