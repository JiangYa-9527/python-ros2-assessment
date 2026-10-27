from glob import glob
import os

from setuptools import find_packages, setup


package_name = "robot_nodes"

setup(
    name=package_name,
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="JiangYa-9527",
    maintainer_email="282097595+JiangYa-9527@users.noreply.github.com",
    description="ROS 2 Python assessment: custom topics, services, launch and parameters.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "robot_status_publisher = robot_nodes.robot_status_publisher:main",
            "robot_status_subscriber = robot_nodes.robot_status_subscriber:main",
            "add_two_ints_server = robot_nodes.add_two_ints_server:main",
            "add_two_ints_client = robot_nodes.add_two_ints_client:main",
        ],
    },
)
