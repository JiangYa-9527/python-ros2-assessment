"""Publish a custom RobotStatus message at the configured frequency."""

import math

from rclpy.node import Node
from robot_interfaces.msg import RobotStatus

from robot_nodes.runtime import spin_node


class RobotStatusPublisher(Node):
    def __init__(self):
        super().__init__("robot_status_publisher")
        self.declare_parameter("publish_frequency", 1.0)
        self.declare_parameter("topic_name", "/robot_status")
        frequency = self.get_parameter("publish_frequency").value
        topic_name = self.get_parameter("topic_name").value
        if not math.isfinite(frequency) or frequency <= 0.0:
            raise ValueError("publish_frequency must be a finite positive number")

        self.publisher = self.create_publisher(RobotStatus, topic_name, 10)
        self.period = 1.0 / frequency
        self.position_x = 0.0
        self.timer = self.create_timer(self.period, self.publish_status)
        self.get_logger().info(
            f"Publishing {self.publisher.topic_name} at {frequency:g} Hz"
        )

    def publish_status(self):
        message = RobotStatus()
        message.robot_name = "robot_demo"
        message.speed = 0.5
        message.position_x = self.position_x
        message.position_y = 0.0
        self.publisher.publish(message)
        self.get_logger().info(
            f"Published name={message.robot_name}, speed={message.speed:.2f}, "
            f"position=({message.position_x:.2f}, {message.position_y:.2f})"
        )
        self.position_x += message.speed * self.period


def main(args=None):
    spin_node(RobotStatusPublisher, args)


if __name__ == "__main__":
    main()
