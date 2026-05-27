#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class SpiralTurtle(Node):

    def __init__(self):

        super().__init__('spiral_turtle')

        # Publisher to control turtle movement
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Timer calls move_turtle every 0.1 seconds
        self.timer = self.create_timer(
            0.1,
            self.move_turtle
        )

        # Initial speeds
        self.linear_speed = 0.5
        self.angular_speed = 1.0

    def move_turtle(self):

        msg = Twist()

        # Increase forward speed slowly
        self.linear_speed += 0.02

        # Forward movement
        msg.linear.x = self.linear_speed

        # Turning movement
        msg.angular.z = self.angular_speed

        # Publish movement command
        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Linear Speed: {self.linear_speed:.2f}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = SpiralTurtle()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()