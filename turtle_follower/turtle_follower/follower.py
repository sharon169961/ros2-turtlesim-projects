#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

from turtlesim.srv import Spawn
from turtlesim.srv import SetPen

import math
import random


class TurtleFollower(Node):

    def __init__(self):

        super().__init__('turtle_follower')

        # Store poses
        self.leader_pose = None
        self.follower_pose = None

        # Publisher to move turtle2
        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle2/cmd_vel',
            10
        )

        # Spawn service client
        self.spawn_client = self.create_client(
            Spawn,
            '/spawn'
        )

        # Pen service client
        self.pen_client = self.create_client(
            SetPen,
            '/turtle2/set_pen'
        )

        # Wait for spawn service
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn service...')

        # Spawn follower turtle
        self.spawn_follower()

        # Subscribe to leader pose
        self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.leader_callback,
            10
        )

        # Subscribe to follower pose
        self.create_subscription(
            Pose,
            '/turtle2/pose',
            self.follower_callback,
            10
        )

        # Main loop timer
        self.timer = self.create_timer(
            0.1,
            self.follow_leader
        )

    # Spawn turtle2
    def spawn_follower(self):

        request = Spawn.Request()

        request.x = 5.0
        request.y = 5.0
        request.theta = 0.0
        request.name = 'turtle2'

        self.spawn_client.call_async(request)

    # Leader pose callback
    def leader_callback(self, msg):

        self.leader_pose = msg

    # Follower pose callback
    def follower_callback(self, msg):

        self.follower_pose = msg

    # Main following logic
    def follow_leader(self):

        if self.leader_pose is None:
            return

        if self.follower_pose is None:
            return

        # Leader position
        x1 = self.leader_pose.x
        y1 = self.leader_pose.y

        # Follower position
        x2 = self.follower_pose.x
        y2 = self.follower_pose.y

        # Distance to leader
        distance = math.sqrt(
            (x1 - x2)**2 +
            (y1 - y2)**2
        )

        # Direction to leader
        target_angle = math.atan2(
            y1 - y2,
            x1 - x2
        )

        # Angle difference
        angle_error = (
            target_angle -
            self.follower_pose.theta
        )

        # Create movement message
        msg = Twist()

        # Proportional control
        msg.linear.x = 1.5 * distance
        msg.angular.z = 6.0 * angle_error

        # Move follower turtle
        self.cmd_pub.publish(msg)

        # Change pen color
        self.change_pen_color()

    # Random pen colors
    def change_pen_color(self):

        if not self.pen_client.wait_for_service(timeout_sec=1.0):
            return

        request = SetPen.Request()

        request.r = random.randint(0, 255)
        request.g = random.randint(0, 255)
        request.b = random.randint(0, 255)

        request.width = 3
        request.off = 0

        self.pen_client.call_async(request)


def main(args=None):

    rclpy.init(args=args)

    node = TurtleFollower()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()



