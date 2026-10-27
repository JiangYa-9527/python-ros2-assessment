"""Receive RobotStatus and print its name, speed and coordinates."""

from rclpy.node import Node
from robot_interfaces.msg import RobotStatus

from robot_nodes.runtime import spin_node


class RobotStatusSubscriber(Node):
    def __init__(self):
        super().__init__("robot_status_subscriber")
        self.declare_parameter("topic_name", "/robot_status")
        topic_name = self.get_parameter("topic_name").value
        self.subscription = self.create_subscription(
            RobotStatus, topic_name, self.status_callback, 10
        )
        self.get_logger().info(f"Subscribed to {self.subscription.topic_name}")

    def status_callback(self, message):
        self.get_logger().info(
            f"Received name={message.robot_name}, speed={message.speed:.2f}, "
            f"position=({message.position_x:.2f}, {message.position_y:.2f})"
        )


def main(args=None):
    spin_node(RobotStatusSubscriber, args)


if __name__ == "__main__":
    main()
