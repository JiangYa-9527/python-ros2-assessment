"""Send one request by default; launch config enables repeated requests."""

import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from robot_interfaces.srv import AddTwoInts

from robot_nodes.add_two_ints_server import INT64_MAX, INT64_MIN


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__("add_two_ints_client")
        self.declare_parameter("service_name", "/add_two_ints")
        self.declare_parameter("a", 3)
        self.declare_parameter("b", 5)
        self.declare_parameter("repeat", False)
        self.declare_parameter("request_period", 2.0)

        service_name = self.get_parameter("service_name").value
        self.a = self.get_parameter("a").value
        self.b = self.get_parameter("b").value
        self.repeat = self.get_parameter("repeat").value
        period = self.get_parameter("request_period").value
        if not math.isfinite(period) or period <= 0.0:
            raise ValueError("request_period must be a finite positive number")
        if not INT64_MIN <= self.a + self.b <= INT64_MAX:
            raise ValueError("a + b must fit in the int64 service response")

        self.client = self.create_client(AddTwoInts, service_name)
        self.future = None
        self.done = False
        self.failed = False
        self.timer = self.create_timer(period, self.send_request)
        self.get_logger().info(f"Client using service {self.client.srv_name}")

    def send_request(self):
        if self.future is not None:
            return
        if not self.client.service_is_ready():
            self.get_logger().info("Waiting for add_two_ints service...", throttle_duration_sec=5.0)
            return

        request = AddTwoInts.Request()
        request.a = self.a
        request.b = self.b
        self.future = self.client.call_async(request)
        self.future.add_done_callback(self.receive_response)

    def receive_response(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Result: {self.a} + {self.b} = {response.sum}")
        except Exception as error:
            self.failed = True
            self.get_logger().error(f"Service request failed: {error}")
        finally:
            self.future = None
            if not self.repeat:
                self.done = True
                self.timer.cancel()


def main(args=None):
    rclpy.init(args=args)
    node = None
    failed = False
    try:
        node = AddTwoIntsClient()
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.5)
        failed = node.failed
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
