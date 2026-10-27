#!/usr/bin/env python3
"""Verify the real ROS 2 graph after sourcing ROS and the built workspace.

Usage: python3 scripts/verify_ros2.py [--ns robot1] [--node-name atil_1]
Requires ros2, the installed robot_nodes/robot_interfaces packages, and PyYAML.
"""

import argparse
import math
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time


def stop_process(process):
    """Interrupt our process group, with bounded terminate/kill fallbacks."""
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGINT)
        else:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        process.wait(timeout=5)
    except (ProcessLookupError, OSError, subprocess.TimeoutExpired):
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            process.wait(timeout=2)
        except (ProcessLookupError, OSError, subprocess.TimeoutExpired):
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            process.wait(timeout=2)


def verify(args):
    if shutil.which("ros2") is None:
        raise RuntimeError("ros2 is unavailable; source ROS 2 and install/setup.bash first")
    import yaml

    environment = os.environ.copy()
    # Keep a caller-selected domain, or isolate this run from unrelated robots.
    environment.setdefault("ROS_DOMAIN_ID", str(secrets.randbelow(100) + 1))
    environment["PYTHONUNBUFFERED"] = "1"
    environment["RCUTILS_COLORIZED_OUTPUT"] = "0"
    group = {"start_new_session": True} if os.name == "posix" else {
        "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP
    }
    deadline = time.monotonic() + args.timeout
    logs = []
    launch_process = subprocess.Popen(
        ["ros2", "launch", "robot_nodes", "robot_system.launch.py",
         f"ns:={args.namespace}", f"node_name:={args.node_name}"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace", env=environment, **group,
    )

    def collect_logs():
        for line in launch_process.stdout:
            logs.append(line)

    reader = threading.Thread(target=collect_logs, daemon=True)
    reader.start()

    def command(*arguments, timeout=8):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("overall verification timeout exceeded")
        if launch_process.poll() is not None:
            raise RuntimeError(f"launch exited early with status {launch_process.returncode}")
        process = subprocess.Popen(
            ["ros2", *arguments], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8",
            errors="replace", env=environment, **group,
        )
        try:
            output, _ = process.communicate(timeout=min(timeout, remaining))
        except subprocess.TimeoutExpired as error:
            stop_process(process)
            output, _ = process.communicate()
            raise RuntimeError(f"ros2 {' '.join(arguments)} timed out:\n{output}") from error
        finally:
            if process.poll() is None:
                stop_process(process)
        if process.returncode:
            raise RuntimeError(f"ros2 {' '.join(arguments)} failed:\n{output}")
        return output

    namespace = args.namespace.strip("/")

    def full_name(name):
        return "/" + "/".join(part for part in (namespace, name) if part)

    try:
        expected = {full_name(name) for name in (
            args.node_name, "robot_status_subscriber",
            "add_two_ints_server", "add_two_ints_client",
        )}
        discovery_deadline = min(deadline, time.monotonic() + 18)
        while True:
            node_output = command("node", "list", "--no-daemon", "--spin-time", "1")
            if expected.issubset(set(node_output.splitlines())):
                break
            if time.monotonic() >= discovery_deadline:
                raise RuntimeError(f"nodes missing: {sorted(expected - set(node_output.splitlines()))}")
            time.sleep(0.3)
        print("PASS: four expected nodes discovered", flush=True)

        topic = full_name("robot_status")
        service = full_name("add_two_ints")
        # DDS discovers endpoints asynchronously, independently of node names.
        # Keep checking for the expected types until a bounded discovery deadline.
        type_deadline = min(deadline, time.monotonic() + 18)
        while True:
            topics = command("topic", "list", "-t", "--no-daemon", "--spin-time", "2")
            services = command("service", "list", "-t", "--no-daemon", "--spin-time", "2")
            topic_ready = f"{topic} [robot_interfaces/msg/RobotStatus]" in topics.splitlines()
            service_ready = f"{service} [robot_interfaces/srv/AddTwoInts]" in services.splitlines()
            if topic_ready and service_ready:
                break
            if time.monotonic() >= type_deadline:
                raise RuntimeError(f"custom topic/service types missing:\n{topics}\n{services}")
        print("PASS: custom topic and service types discovered", flush=True)

        output = command("topic", "echo", topic, "robot_interfaces/msg/RobotStatus", "--once", timeout=10)
        messages = [item for item in yaml.safe_load_all(output) if isinstance(item, dict)]
        if not messages:
            raise RuntimeError(f"no RobotStatus message received:\n{output}")
        message = messages[0]
        if message.get("robot_name") != "robot_demo":
            raise RuntimeError(f"unexpected robot_name: {message}")
        for key in ("speed", "position_x", "position_y"):
            value = message.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise RuntimeError(f"invalid numeric field {key}: {message}")
        if not math.isclose(message["speed"], 0.5) or message["position_x"] < 0 or message["position_y"] != 0:
            raise RuntimeError(f"unexpected status values: {message}")
        print("PASS: received valid RobotStatus fields", flush=True)

        response = command("service", "call", service, "robot_interfaces/srv/AddTwoInts", "{a: 3, b: 5}", timeout=10)
        if not re.search(r"\bsum\s*[=:]\s*8\b", response):
            raise RuntimeError(f"3 + 5 did not return sum=8:\n{response}")
        for attempt in range(3):
            try:
                frequency = command(
                    "param", "get", full_name(args.node_name), "publish_frequency",
                    "--no-daemon", "--spin-time", "2", "--timeout", "5", timeout=10,
                )
                break
            except RuntimeError as error:
                if "Node not found" not in str(error) or attempt == 2:
                    raise
                time.sleep(0.5)
        if not re.search(r"\bvalue\s+is:\s*1\.0\b", frequency):
            raise RuntimeError(f"publish_frequency was not loaded as 1.0:\n{frequency}")
        print("PASS: service returns 8 and YAML publish_frequency is 1.0", flush=True)

        while True:
            log_text = "".join(logs)
            if "Received name=robot_demo, speed=" in log_text and "Result: 3 + 5 = 8" in log_text:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("subscriber callback or client response log was not observed")
            if launch_process.poll() is not None:
                raise RuntimeError("launch exited while waiting for callback logs")
            time.sleep(0.1)
        print("PASS: subscriber callback and launched client response observed", flush=True)
        # Verify actual timer behavior as well as the configured frequency.
        while True:
            publish_times = [float(match.group(1)) for line in logs
                             if "Published name=robot_demo," in line
                             for match in [re.search(r"\[([0-9]+\.[0-9]+)\]", line)]
                             if match]
            if len(publish_times) >= 3:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("not enough publication timestamps to measure 1 Hz")
            time.sleep(0.1)
        mean_period = (publish_times[-1] - publish_times[0]) / (len(publish_times) - 1)
        if not 0.75 <= mean_period <= 1.25:
            raise RuntimeError(f"publication period is {mean_period:.3f}s; expected about 1s")
        print(f"PASS: measured publication rate {1.0 / mean_period:.3f} Hz", flush=True)
        print(f"ROS 2 verification passed (ROS_DOMAIN_ID={environment['ROS_DOMAIN_ID']}).", flush=True)
    except Exception:
        print("--- captured ros2 launch output ---\n" + "".join(logs), file=sys.stderr)
        raise
    finally:
        stop_process(launch_process)
        reader.join(timeout=2)
        launch_process.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ns", "--namespace", dest="namespace", default="robot1")
    parser.add_argument("--node-name", default="atil_1")
    parser.add_argument("--timeout", type=float, default=45.0)
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be a finite positive number")
    try:
        verify(args)
    except (Exception, KeyboardInterrupt) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
