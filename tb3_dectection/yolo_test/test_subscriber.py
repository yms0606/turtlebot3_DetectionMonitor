
import rclpy
from rclpy.node import Node
import rclpy.subscription
from yolo_topic_msg.msg import DaTopic
from rclpy.qos import QoSDurabilityPolicy
from rclpy.qos import QoSHistoryPolicy
from rclpy.qos import QoSProfile
from rclpy.qos import QoSReliabilityPolicy



class YoloSubscriber(Node):
    
    qos_profile = QoSProfile(
        depth=10,
    )
    def __init__(self):

        super().__init__('yolo_subscriber')
        
        self.data = DaTopic()
        self.subscription = self.create_subscription(DaTopic,'topic',
                                                       self.listener_callback,qos_profile=qos_profile)
        self.subscription
    
    def listener_callback(self,msg):
        self.data=msg
        #self.get_logger().info(f"msg.x: {msg.x}, msg.y:{msg.y}")


def main(args=None):
    rclpy.init(args=args)

    yolo_subscriber = YoloSubscriber()

    rclpy.spin(yolo_subscriber)

    yolo_subscriber.destory_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()