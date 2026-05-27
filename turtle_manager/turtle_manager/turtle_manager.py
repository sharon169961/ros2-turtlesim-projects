#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from turtlesim.srv import Spawn
from turtlesim.srv import Kill

import random


class TurtleManager(Node):

    def __init__(self):

        super().__init__('turtle_manager')

        # Create service clients
        self.spawn_client = self.create_client(
            Spawn,
            '/spawn'
        )

        self.kill_client = self.create_client(
            Kill,
            '/kill'
        )

        # Wait for services
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn service...')

        while not self.kill_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for kill service...')

        # Store turtle names
        self.turtle_list = []

        # Turtle counter
        self.counter = 2

        # Run every 1 second
        self.timer = self.create_timer(
            1.0,
            self.manage_turtles
        )

    def manage_turtles(self):

        # Random position
        x = random.uniform(1.0, 10.0)
        y = random.uniform(1.0, 10.0)
        theta = random.uniform(0.0, 6.28)

        # Turtle name
        turtle_name = f'turtle{self.counter}'
        self.counter += 1

        # Create spawn request
        request = Spawn.Request()

        request.x = x
        request.y = y
        request.theta = theta
        request.name = turtle_name

        # Call spawn service asynchronously
        self.spawn_client.call_async(request)

        # Log message
        self.get_logger().info(
            f'Spawned {turtle_name}'
        )

        # Store turtle
        self.turtle_list.append(turtle_name)

        # Kill oldest turtle if more than 2 exist
        if len(self.turtle_list) > 2:

            oldest_turtle = self.turtle_list.pop(0)

            kill_request = Kill.Request()

            kill_request.name = oldest_turtle

            # Call kill service asynchronously
            self.kill_client.call_async(kill_request)

            self.get_logger().info(
                f'Killed {oldest_turtle}'
            )


def main(args=None):

    rclpy.init(args=args)

    node = TurtleManager()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()