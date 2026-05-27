#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

from turtlesim.srv import Spawn
from turtlesim.srv import Kill

import math
import random


class TurtleHunter(Node):

    def __init__(self):

        super().__init__('turtle_hunter')

        # Publisher to move turtle1
        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Subscribe to turtle1 pose
        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # Service clients
        self.spawn_client = self.create_client(
            Spawn,
            '/spawn'
        )

        self.kill_client = self.create_client(
            Kill,
            '/kill'
        )

        # Current hunter pose
        self.hunter_pose = None

        # Target turtle info
        self.target_name = None
        self.target_pose = None

        # Counter
        self.counter = 2

        # Spawn turtles every 5 seconds
        self.spawn_timer = self.create_timer(
            5.0,
            self.spawn_turtle
        )

        # Hunter logic loop
        self.control_timer = self.create_timer(
            0.1,
            self.hunt_target
        )

    # Updates turtle1 pose
    def pose_callback(self, msg):

        self.hunter_pose = msg

    # Spawn enemy turtle
    def spawn_turtle(self):

        x = random.uniform(1.0, 10.0)
        y = random.uniform(1.0, 10.0)
        theta = random.uniform(0.0, 6.28)

        turtle_name = f'turtle{self.counter}'
        self.counter += 1

        request = Spawn.Request()

        request.x = x
        request.y = y
        request.theta = theta
        request.name = turtle_name

        self.spawn_client.call_async(request)

        self.get_logger().info(
            f'Spawned {turtle_name}'
        )

        # Subscribe to target pose
        self.create_subscription(
            Pose,
            f'/{turtle_name}/pose',
            self.target_callback,
            10
        )

        # Set first target
        if self.target_name is None:
            self.target_name = turtle_name

    # Updates target pose
    def target_callback(self, msg):

        self.target_pose = msg

    # Main hunting logic
    def hunt_target(self):

        if self.hunter_pose is None:
            return

        if self.target_pose is None:
            return

        # Hunter position
        x1 = self.hunter_pose.x
        y1 = self.hunter_pose.y

        # Target position
        x2 = self.target_pose.x
        y2 = self.target_pose.y

        # Distance formula
        distance = math.sqrt(
            (x2 - x1)**2 +
            (y2 - y1)**2
        )

        # Target angle
        target_angle = math.atan2(
            y2 - y1,
            x2 - x1
        )

        # Angle error
        angle_error = (
            target_angle -
            self.hunter_pose.theta
        )

        # Create movement command
        msg = Twist()

        # Proportional controller
        msg.linear.x = 1.5 * distance
        msg.angular.z = 6.0 * angle_error

        # Publish movement
        self.cmd_pub.publish(msg)

        # Kill turtle if close
        if distance < 0.5 and self.target_name is not None:

            caught_turtle = self.target_name

            kill_request = Kill.Request()

            kill_request.name = caught_turtle

            self.kill_client.call_async(kill_request)

            self.get_logger().info(
                f'Caught {caught_turtle}'
            )

            self.target_name = None
            self.target_pose = None


def main(args=None):

    rclpy.init(args=args)

    node = TurtleHunter()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()