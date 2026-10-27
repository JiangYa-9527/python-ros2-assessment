"""Static package contracts only; these checks do not run or simulate ROS 2."""

import ast
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exam2" / "ros2_ws" / "src"
INTERFACES = SOURCE / "robot_interfaces"
NODES = SOURCE / "robot_nodes"
EXECUTABLES = {
    "robot_status_publisher",
    "robot_status_subscriber",
    "add_two_ints_server",
    "add_two_ints_client",
}


def interface_lines(path):
    return [
        line.split("#", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.split("#", 1)[0].strip()
    ]


class InterfaceContractTests(unittest.TestCase):
    def test_robot_status_field_types_and_order(self):
        self.assertEqual(
            interface_lines(INTERFACES / "msg" / "RobotStatus.msg"),
            [
                "string robot_name",
                "float32 speed",
                "float32 position_x",
                "float32 position_y",
            ],
        )

    def test_service_request_response_contract(self):
        self.assertEqual(
            interface_lines(INTERFACES / "srv" / "AddTwoInts.srv"),
            ["int64 a", "int64 b", "---", "int64 sum"],
        )

    def test_interface_generation_dependencies(self):
        package = ET.parse(INTERFACES / "package.xml").getroot()
        self.assertEqual(package.findtext("name"), "robot_interfaces")
        self.assertEqual(package.findtext("export/build_type"), "ament_cmake")
        self.assertIn(
            "rosidl_default_generators",
            [element.text for element in package.findall("buildtool_depend")],
        )
        self.assertIn(
            "rosidl_default_runtime",
            [element.text for element in package.findall("exec_depend")],
        )
        self.assertIn(
            "rosidl_interface_packages",
            [element.text for element in package.findall("member_of_group")],
        )
        cmake = (INTERFACES / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("rosidl_generate_interfaces(", cmake)
        self.assertIn('"msg/RobotStatus.msg"', cmake)
        self.assertIn('"srv/AddTwoInts.srv"', cmake)


class NodePackageTests(unittest.TestCase):
    def test_runtime_dependencies_and_package_resources(self):
        package = ET.parse(NODES / "package.xml").getroot()
        self.assertEqual(package.findtext("name"), "robot_nodes")
        self.assertEqual(package.findtext("export/build_type"), "ament_python")
        dependencies = {element.text for element in package.findall("exec_depend")}
        self.assertTrue(
            {
                "rclpy", "robot_interfaces", "ament_index_python",
                "launch", "launch_ros", "python3-yaml",
            }.issubset(dependencies)
        )
        for resource in (
            "resource/robot_nodes", "robot_nodes/__init__.py", "setup.cfg",
            "launch/robot_system.launch.py", "config/params.yaml",
        ):
            self.assertTrue((NODES / resource).is_file(), resource)

    def test_four_installed_console_entrypoints_have_main_functions(self):
        tree = ast.parse((NODES / "setup.py").read_text(encoding="utf-8"))
        setup_call = next(
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name) and node.func.id == "setup"
        )
        entrypoints = ast.literal_eval(next(
            keyword.value for keyword in setup_call.keywords
            if keyword.arg == "entry_points"
        ))["console_scripts"]
        installed = {}
        for entrypoint in entrypoints:
            name, target = map(str.strip, entrypoint.split("=", 1))
            module, function = target.split(":", 1)
            module_file = NODES.joinpath(*module.split(".")).with_suffix(".py")
            module_tree = ast.parse(module_file.read_text(encoding="utf-8"))
            self.assertTrue(any(
                isinstance(item, ast.FunctionDef) and item.name == function
                for item in module_tree.body
            ), target)
            installed[name] = target
        self.assertEqual(set(installed), EXECUTABLES)

    def test_python_sources_compile_without_importing_ros(self):
        sources = list(SOURCE.rglob("*.py"))
        self.assertTrue(sources)
        for source in sources:
            with self.subTest(source=str(source.relative_to(ROOT))):
                compile(source.read_text(encoding="utf-8"), str(source), "exec")

    def test_default_yaml_node_names_and_communication_names_match(self):
        # This intentionally checks the committed, simple YAML's structure as
        # text. Parsing and applying YAML is part of the real ROS smoke test.
        yaml_text = (NODES / "config" / "params.yaml").read_text(encoding="utf-8")
        blocks = {}
        current = None
        for line in yaml_text.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            top_level = re.fullmatch(r"([A-Za-z_][A-Za-z_0-9]*):", line)
            if top_level:
                current = top_level.group(1)
                blocks[current] = []
            else:
                self.assertIsNotNone(current, "YAML content before node key")
                blocks[current].append(line)
        self.assertEqual(set(blocks), {
            "atil_1", "robot_status_subscriber",
            "add_two_ints_server", "add_two_ints_client",
        })
        for lines in blocks.values():
            self.assertIn("  ros__parameters:", lines)
        self.assertIn("    publish_frequency: 1.0", blocks["atil_1"])
        self.assertIn("    topic_name: robot_status", blocks["atil_1"])
        self.assertIn("    topic_name: robot_status", blocks["robot_status_subscriber"])
        for name in ("add_two_ints_server", "add_two_ints_client"):
            self.assertIn("    service_name: add_two_ints", blocks[name])
        self.assertIn("    repeat: true", blocks["add_two_ints_client"])

    def test_launch_defaults_and_screen_output(self):
        path = NODES / "launch" / "robot_system.launch.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        arguments = {}
        node_calls = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id == "DeclareLaunchArgument":
                name = ast.literal_eval(node.args[0])
                defaults = {keyword.arg: keyword.value for keyword in node.keywords}
                if isinstance(defaults.get("default_value"), ast.Constant):
                    arguments[name] = ast.literal_eval(defaults["default_value"])
            elif node.func.id == "Node":
                node_calls.append(node)
        self.assertEqual(arguments["ns"], "robot1")
        self.assertEqual(arguments["node_name"], "atil_1")
        self.assertTrue(node_calls)
        for node_call in node_calls:
            keywords = {keyword.arg: keyword.value for keyword in node_call.keywords}
            self.assertEqual(ast.literal_eval(keywords["output"]), "screen")
            self.assertIn("namespace", keywords)
            self.assertIn("parameters", keywords)
        # All four executables must be represented in the launch plan.
        string_constants = {
            node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        self.assertTrue(EXECUTABLES.issubset(string_constants))


if __name__ == "__main__":
    unittest.main()
