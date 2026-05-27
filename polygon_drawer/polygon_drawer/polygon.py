#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen

import math
import random
import time


class PolygonDrawer(Node):

    def __init__(self):

        super().__init__('polygon_drawer')

        # Publisher
        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Pose subscriber
        self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # Pen service
        self.pen_client = self.create_client(
            SetPen,
            '/turtle1/set_pen'
        )

        # Current pose
        self.pose = None

        # User input
        self.sides = int(input("Enter number of sides: "))
        self.length = float(input("Enter side length: "))

        # Polygon exterior angle
        self.angle = 360 / self.sides

        # Small delay
        time.sleep(2)

        # Start drawing
        self.draw_polygon()

    # Pose callback
    def pose_callback(self, msg):

        self.pose = msg

    # Move turtle forward
    def move_forward(self):

        msg = Twist()

        msg.linear.x = self.length
        msg.angular.z = 0.0

        self.cmd_pub.publish(msg)

        time.sleep(1)

        self.stop_turtle()

    # Rotate turtle
    def rotate(self):

        msg = Twist()

        msg.linear.x = 0.0

        # Convert angle to radians
        msg.angular.z = math.radians(self.angle)

        self.cmd_pub.publish(msg)

        time.sleep(1)

        self.stop_turtle()

    # Stop turtle
    def stop_turtle(self):

        msg = Twist()

        self.cmd_pub.publish(msg)

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

    # Draw polygon
    def draw_polygon(self):

        for _ in range(self.sides):

            self.change_pen_color()

            self.move_forward()

            self.rotate()

        self.get_logger().info('Polygon completed!')


def main(args=None):

    rclpy.init(args=args)

    node = PolygonDrawer()

    rclpy.spin_once(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':

    main()