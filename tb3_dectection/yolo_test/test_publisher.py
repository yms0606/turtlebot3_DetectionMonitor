import rclpy
from rclpy.node import Node
from yolo_topic_msg.msg import DaTopic
from geometry_msgs.msg import PoseStamped
import time

i = -1

class YoloPublisher(Node):
    def __init__(self):

        super().__init__('yolo_publisher')

        #self._publishers = self.create_publisher(DaTopic, 'topic', 10)

        
        self.x = 0.0
        self.y = 0.0


        self.pub_pose = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.pose = PoseStamped()
        self.pose.header.stamp = self.get_clock().now().to_msg()
        self.pose.header.frame_id = 'map'
        self.pose.pose.position.x = 0.03
        self.pose.pose.position.y = -0.001
        #self.pose.pose.position.x = 0.73
        #self.pose.pose.position.y = -0.06

        self.pose.pose.orientation.x = 0.0
        self.pose.pose.orientation.y = 0.0
        self.pose.pose.orientation.z = 0.0
        self.pose.pose.orientation.w = 0.0

        self.timer = self.create_timer(1, self.pub)
        #self.pub()

    def pub(self):
        global i
        for _ in range(5):
            self.pub_pose.publish(self.pose)
            time.sleep(0.05)
            self.get_logger().info(f"pub success {i}")
            i += 1


def main(args=None):

    rclpy.init(args=args)
    yolo_publisher = YoloPublisher()
    rclpy.spin(yolo_publisher)

    yolo_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
