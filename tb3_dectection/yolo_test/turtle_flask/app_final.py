from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import cv2
import sqlite3
from datetime import datetime
import threading
import rclpy
from rclpy.node import Node
import rclpy.subscription
from rcl_interfaces.msg import Log
from yolo_topic_msg.msg import DaTopic, Video, Id
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile
import numpy as np
import time
import os
import json
import math

os.environ["ROS_DOMAIN_ID"] = "4"

ros2_image = None
numpy_img = None

ros2_data = {'x':-1.0, 'y':-1.0}
Istrack = False
node = None

qos_profile = QoSProfile(
        depth=10,
    )

app = Flask(__name__)

class SystemNode(Node):
    def __init__(self):
        super().__init__('yolo_subscriber')
        self.bridge = CvBridge()
        self.data = DaTopic()
        self.video = Video()
        
        self.subscription = self.create_subscription(DaTopic,'topic', self.listener_callback, qos_profile=qos_profile)
        self.subscription
        
        self.sub_image = self.create_subscription(CompressedImage, 'image', self.image_callback, qos_profile=qos_profile)
        self.sub_image

        self.sub_status = self.create_subscription(Log,'rosout', self.status_callback, qos_profile=qos_profile)
        self.sub_status

        self.pub_id = self.create_publisher(Id, 'track_id', 10)

        self.get_logger().info("success sub")

    #NEW
    def status_callback(self, msg):
        if 'goal success' in msg.msg:
            chase()

    def image_callback(self, msg):
        global ros2_image
        ros2_image = self.bridge.compressed_imgmsg_to_cv2(msg)

    def listener_callback(self, msg):
        global ros2_data
        ros2_data['x'] = round(msg.x, 3)
        ros2_data['y'] = round(msg.y, 3)
        self.get_logger().info(f"msg.x: {ros2_data['x']}, msg.y:{ros2_data['y']}")


    def video_callback(self, msg):
        global ros2_image, numpy_img

        ros2_image = np.array(msg.video_file, dtype=np.uint8)
        numpy_img = ros2_image.reshape((msg.height, msg.width, msg.channels))


# 데이터베이스 초기화 함수
def init_db():
    conn = sqlite3.connect('chase_records.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chase (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT,
                    timestamp TEXT)''')
    conn.commit()
    conn.close()

# 데이터베이스에 추격 기록 추가
def add_chase_record(vehicle_id):
    conn = sqlite3.connect('chase_records.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO chase (vehicle_id, timestamp) VALUES (?, ?)', (vehicle_id, timestamp))
    conn.commit()
    conn.close()


# ROS2 쓰레드
def ros2_thread():
    global node, ros2_image
    
    rclpy.init()
    node = SystemNode()

    while rclpy.ok():
        rclpy.spin_once(node)


# # 카메라 캡처 객체 생성
# cctv_capture = cv2.VideoCapture(0)  # 노트북의 기본 웹캠
# turtlebot_capture = cv2.VideoCapture(2)  # 터틀봇 카메라 (외부 카메라)

# # 해상도 설정 (640x480)
# cctv_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cctv_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# turtlebot_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# turtlebot_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# 이미지 스트리밍을 위한 프레임 생성
def generate_frames():
    global ros2_image
    while True:

        if ros2_image is not None:

            ret, jpeg = cv2.imencode('.jpg', ros2_image)
            if ret:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            else:
                break
            time.sleep(0.01)

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
    def generate():
        global ros2_data
        while True:
            yield f"data: {json.dumps(ros2_data)}\n\n"
            time.sleep(1.5)
    return Response(generate(), mimetype='text/event-stream')


@app.route('/stream/cctv')
def stream_cctv():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream/turtlebot')
def stream_turtlebot():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/command', methods=['POST'])
def command():
    data = request.json
    vehicle_id = data.get('vehicle_id', '')
    if vehicle_id:
        add_chase_record(vehicle_id)
    
        msg = Id()
        msg.track_id = int(vehicle_id)
        node.pub_id.publish(msg)

        return jsonify({"status": "success", "message": f"명령이 차량 {vehicle_id}으로 전송되었습니다."})
    
    else:
        return jsonify({"status": "error", "message": "차량 ID가 입력되지 않았습니다."})


@app.route('/get_chase_records')
def get_chase_records():
    conn = sqlite3.connect('chase_records.db')
    c = conn.cursor()
    c.execute('SELECT * FROM chase ORDER BY timestamp DESC')
    records = c.fetchall()
    conn.close()
    return jsonify(records)
    
@app.route('/delete_chase_record', methods=['POST'])
def delete_chase_record():
    record_id = request.json.get('record_id')
    if record_id:
        # 해당 ID를 가진 추격 기록을 삭제
        conn = sqlite3.connect('chase_records.db')
        c = conn.cursor()
        c.execute('DELETE FROM chase WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"추격 기록 {record_id}이 삭제되었습니다."})
    else:
        return jsonify({"status": "error", "message": "유효한 기록 ID가 없습니다."})

#NEW
@app.route('/chase')
def chase():
    def event_stream():
        yield "data :return\n\n"
        time.sleep(0.05)
    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port="5000", threaded=True)

