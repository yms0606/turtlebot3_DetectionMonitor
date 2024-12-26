from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import cv2

import threading
import rclpy
from rclpy.node import Node
import rclpy.subscription
from yolo_topic_msg.msg import DaTopic, Video
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile
import numpy as np
import time
import os

os.environ["ROS_DOMAIN_ID"] = "10"

ros2_image = None
numpy_img = None
ros2_data = []
#ros2_lock = threading.Lock()

qos_profile = QoSProfile(
        depth=10,
    )

class YoloSubscriber(Node):
    
    def __init__(self):

        super().__init__('yolo_subscriber')
        

        self.bridge = CvBridge()
        self.data = DaTopic()
        self.video = Video()
        self.subscription = self.create_subscription(DaTopic,'topic',
                                                       self.listener_callback,qos_profile=qos_profile)
        self.subscription

        #self.sub_video = self.create_subscription(Video, 'video', self.video_callback, qos_profile=qos_profile)

        #self.sub_video

        self.sub_image = self.create_subscription(CompressedImage, 'image',self.image_callback,qos_profile=qos_profile)
        self.sub_image

        self.get_logger().info("success sub")
    
    def image_callback(self, msg):
        global ros2_image
        ros2_image = self.bridge.compressed_imgmsg_to_cv2(msg)

    def listener_callback(self,msg):
        self.data=msg
        #self.get_logger().info(f"msg.x: {msg.x}, msg.y:{msg.y}")

    def video_callback(self, msg):
        global ros2_image,numpy_img

        #self.get_logger().info("success callback")

        ros2_image = np.array(msg.video_file, dtype = np.uint8)
        numpy_img = ros2_image.reshape((msg.height, msg.width, msg.channels))

        #self.get_logger().info(f"{numpy_img.shape}")

app = Flask(__name__)

# 카메라 설정
'''
cctv_capture = cv2.VideoCapture(temp_video)
turtlebot_capture = cv2.VideoCapture(0) 

cctv_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cctv_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 384)
turtlebot_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
turtlebot_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
'''

def ros2_thread():
    global ros2_data,ros2_image

    rclpy.init()
    node = YoloSubscriber()

    while rclpy.ok():
        rclpy.spin_once(node)

    


def generate_frames():
    global ros2_image, ros2_data
    while True:
        
        if ros2_image is not None:
            ret, jpeg = cv2.imencode('.jpg', ros2_image)
            if ret:
                #frame = jpeg.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            else:
                break
            time.sleep(0.01)
        #else:
        #    time.sleep(0.1)
            
        #ret, frame = capture.read()
        #if not ret:
        #    break
        #else:
            #ret, buffer = cv2.imencode('.jpg', frame)
            #frame = buffer.tobytes()
            # yield (b'--frame\r\n'
            #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == '1234':
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/index')
def index():
    ros_th = threading.Thread(target=ros2_thread)
    ros_th.daemon = True
    ros_th.start()
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    if len(ros2_data) > 0:
        return jsonify(messsage = ros2_data[-1])
    else:
        return jsonify(message='No data')

@app.route('/stream/cctv')
def stream_cctv():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stream/turtlebot')
def stream_turtlebot():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/command', methods=['POST'])
def command():
    # 클라이언트에서 보낸 데이터 받기
    data = request.json
    vehicle_id = data.get('vehicle_id', '')
    
    # 여기서 터틀봇에 명령 전달 로직 구현
    # 예: ROS 메시지 송신 또는 API 호출
    print(f"터틀봇 명령 실행: 차량 ID = {vehicle_id}")
    
    return jsonify({"status": "success", "message": f"명령이 터틀봇으로 전송되었습니다: {vehicle_id}"})


if __name__ == "__main__":

    app.run(host="127.0.0.1", port="5001",threaded=True)
