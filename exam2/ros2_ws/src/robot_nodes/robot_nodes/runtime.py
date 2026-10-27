"""Shared spinning and Ctrl+C cleanup for the topic and server nodes."""

import rclpy
from rclpy.executors import ExternalShutdownException


def spin_node(node_class, args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = node_class()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
