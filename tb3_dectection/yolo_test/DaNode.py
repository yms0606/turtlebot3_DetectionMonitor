import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from yolo_topic_msg.msg import DaTopic,Video, Id
from rcl_interfaces.msg import Log
from sensor_msgs.msg import Image, CompressedImage
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
import queue
import numpy as np
import os
import math
import threading
import time

idx = -1
msg_daToic = DaTopic()
i = 0

os.environ["ROS_DOMAIN_ID"] = "4"

qos_profile = QoSProfile(
    depth=10,
)

class DaNode(Node):

    def __init__(self):
        
        super().__init__('da_node')

        

        self.glo_x = -1
        self.glo_y = -1
        self.track_id = -1
        self.track_timer = 0.0
        self.Istrack = False


        self.publish_xy = self.create_publisher(DaTopic,'topic',10)
        self.publish_video = self.create_publisher(Video, 'video', 10)
        self.publish_Image = self.create_publisher(CompressedImage,'image',10)

        #NEW
        #self.pubilsh_initpose = self.create_publisher(PoseWithCovarianceStamped, '/initialpose',10)
        self.pubilsh_pose = self.create_publisher(PoseStamped,'/goal_pose', 10)

        self.pose = PoseStamped()
        # self.initpose = PoseWithCovarianceStamped()
        # self.initpose.header.stamp = self.get_clock().now().to_msg()
        # self.initpose.header.frame_id = 'map'
        # self.initpose.pose.pose.position.x = 0.0
        # self.initpose.pose.pose.position.y = 0.0
        # self.initpose.pose.pose.orientation.w = 1.0
        # #NEW
        

        self.subscription_id = self.create_subscription(Id,'track_id', self.callback_track, qos_profile=qos_profile)
        
        #NEW
        self.subccription_status = self.create_subscription(Log,'rosout',self.callback_status, qos_profile= qos_profile)

        self.cap = cv2.VideoCapture(2)
        self.model = YOLO('best.pt')
        

        self.bridge = CvBridge()

        self.msg = DaTopic()
        self.video = Video()

        #NEW
        # for _ in range(5):
        #     self.pubilsh_initpose.publish(self.initpose)
        # self.get_logger().info("publish init pose")


        self.timer = self.create_timer(0.02, self.time_callback)

        #self.detection()

    #NEW
    def cam2digital(self):
        global idx, msg_daToic,i
        campose = [[207, 139], [267,163], [188,187], [170, 235], [212, 333], [151,429],
                   [337, 137], [288, 235], [239,431], [337, 187], [472, 137], [401, 235], [465, 393],
                   [475, 162], [527, 323], [604, 135], [621, 187], [613, 235], [630, 407]]
        digitpose = [[0.03, -0.001], [0.188, -0.09], [-0.017, -0.17], [-0.064, -0.341], [0.052, -0.548], [-0.11, -0.74],
                     [0.37, -0.02],[0.25, -0.341], [0.13, -0.77], [0.37, -0.17], [0.73, -0.04], [0.485, -0.341], [0.6, -0.8],
                     [0.722, -0.105], [0.78, -0.58], [1.09, -0.06], [1.06, -0.17], [1.03, -0.341], [1, -0.84]]
        dists = []

        if self.glo_x != -1:

            x = msg_daToic.x
            y = msg_daToic.y


            for pose in campose:
                dist = (x-pose[0])**2 + (y-pose[1])**2
                dists.append(dist)

            if True: #idx != dists.index(min(dists)):
                d_pose = digitpose[dists.index(min(dists))]

                return d_pose

                self.pose.header.stamp = self.get_clock().now().to_msg()
                self.pose.header.frame_id = 'map'
                self.pose.pose.position.x = round(float(d_pose[0]),3)
                self.pose.pose.position.y = round(float(d_pose[1]),3)

                self.pose.pose.orientation.x = 0.0
                self.pose.pose.orientation.y = 0.0
                self.pose.pose.orientation.z = 0.0
                self.pose.pose.orientation.w = 0.0

                idx = dists.index(min(dists))

                #self.pubilsh_pose.publish(self.pose)
                #self.get_logger().info(f"{self.pose.pose.position.x} {self.pose.pose.position.y}")
                #self.get_logger().info(f"publish pose {i}")
                i += 1

                #for _ in range(10):
                #    self.pubilsh_pose.publish(self.pose)
                #    time.sleep(0.5)
                #    i += 1
                #    self.get_logger().info(f"publish pose {i}")
            
    #NEW


    def callback_status(self, msg):
        log = msg
        if 'goal success' in log.msg:
            self.Istrack = False
            self.get_logger().info('goal success')


    def callback_track(self, msg):
        self.track_id = msg.track_id
        self.Istrack = True

    def time_callback(self):
        
        _, frame = self.cap.read()

        results = self.model.track(frame, persist=True)

        annotationed_frame = results[0].plot()
        
        annotationed_frame = cv2.resize(annotationed_frame,(annotationed_frame.shape[0]//2, annotationed_frame.shape[1]//2))

        self.publish_Image.publish(self.bridge.cv2_to_compressed_imgmsg(annotationed_frame))
        
        if self.Istrack:

            boxes = results[0].boxes.xywh.cpu()

            if results[0].boxes.id == None:
                self.track_timer += 0.03
                self.get_logger().info("can't find target")
                self.get_logger().info(f"{self.track_timer}")
                return
            
            track_ids = results[0].boxes.id.int().cpu().tolist()

            if self.track_id not in track_ids:
                self.track_timer += 0.03
                self.get_logger().info('tarck id is not in track_ids')

            else:
                self.get_logger().info('tracking . . .')
                self.track_timer = 0.0
                idx = track_ids.index(self.track_id)
                x,y,w,h = boxes[idx]
                c_x = x+(w//2)
                c_y = y+(y//2)

                if self.glo_x != c_x or self.glo_y != c_y:
                    
                    self.glo_x = c_x
                    self.glo_y = c_y

                    global msg_daToic
                    #msg_daToic = DaTopic()
                    msg_daToic.x = round(float(c_x) * 0.95,3)
                    msg_daToic.y = round(float(c_y) * 0.68,3)
                    self.publish_xy.publish(msg_daToic)


                    d_pose = self.cam2digital()
                    self.pose.header.stamp = self.get_clock().now().to_msg()
                    self.pose.header.frame_id = 'map'
                    self.pose.pose.position.x =  round(float(d_pose[0]),3)
                    self.pose.pose.position.y =  round(float(d_pose[1]),3)

                    self.pose.pose.orientation.x = 0.0
                    self.pose.pose.orientation.y = 0.0
                    self.pose.pose.orientation.z = 0.0
                    self.pose.pose.orientation.w = 0.0

                    #for _ in range(5):
                    self.pubilsh_pose.publish(self.pose)
                    #    time.sleep(0.05)
                    self.get_logger().info(f"{self.pose.pose.position.x} {self.pose.pose.position.y}")
                    #NEW

                    #ros_th = threading.Thread(target=self.cam2digital)
                    #ros_th.daemon = True
                    #ros_th.start()
                    #self.cam2digital()

                    #self.get_logger().info(f"{msg.x} {msg.y}")
                    

            if self.track_timer > 1.0:
                self.get_logger().info('target is outside of picture')
                self.Istrack = False
                self.track_timer = 0.0


    def detection(self):

        while self.cap.isOpened():
            
            ret, frame = self.cap.read()

            if not ret:
                break

            results = self.model.track(frame, persist=True)

            annotationed_frame = results[0].plot()

            annotationed_frame = cv2.resize(annotationed_frame,(annotationed_frame.shape[0]//2, annotationed_frame.shape[1]//2))

            flattened_frame = annotationed_frame.flatten()
            flattened_frame = flattened_frame.astype(np.uint8).tolist()
            
            #print(annotationed_frame)

            box = results[0].boxes.xywh.cpu()
            if box.dim != 0:
                self.msg.x = 1.0
                self.msg.y = 10.0
                #self.msg.x = float(box[0][0])
                #self.msg.y = float(box[0][1])
            else:
                self.msg.x = 0
                self.msg.y = 0

            
            #print(annotationed_frame)
            self.video.video_file = flattened_frame
            self.video.height = annotationed_frame.shape[0]
            self.video.width = annotationed_frame.shape[1]
            self.video.channels = annotationed_frame.shape[2]

            self.publish_xy.publish(self.msg)
            self.publish_video.publish(self.video)

            #self.get_logger().info(f"{self.msg.x}, {self.msg.y}")
            self.get_logger().info(f"{self.video.height},{self.video.width}, {self.video.channels}")
            #cv2.imshow('img',annotationed_frame)

            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        
        self.cap.release()
        cv2.destroyAllWindows()



def main(args=None):

    rclpy.init(args=args)
    yolo_publisher = DaNode()
    rclpy.spin(yolo_publisher)

    yolo_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
