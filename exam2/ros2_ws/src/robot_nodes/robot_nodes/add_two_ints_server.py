"""Expose /add_two_ints using the custom AddTwoInts service."""

from rclpy.node import Node
from robot_interfaces.srv import AddTwoInts

from robot_nodes.runtime import spin_node


INT64_MIN = -(2 ** 63)
INT64_MAX = 2 ** 63 - 1


class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__("add_two_ints_server")
        self.declare_parameter("service_name", "/add_two_ints")
        service_name = self.get_parameter("service_name").value
        self.service = self.create_service(
            AddTwoInts, service_name, self.add_callback
        )
        self.get_logger().info(f"Service ready: {self.service.srv_name}")

    def add_callback(self, request, response):
        total = request.a + request.b
        if not INT64_MIN <= total <= INT64_MAX:
            # The required interface has no error field. Reject unrepresentable sums.
            self.get_logger().error("a + b exceeds the AddTwoInts int64 response range")
            raise OverflowError("a + b must fit in int64")
        response.sum = total
        self.get_logger().info(f"{request.a} + {request.b} = {response.sum}")
        return response


def main(args=None):
    spin_node(AddTwoIntsServer, args)


if __name__ == "__main__":
    main()
