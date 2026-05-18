import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import socket
import cv2
import threading
import time

class DroneConnector(Node):
    def __init__(self):
        super().__init__('drone_connector')
        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.bridge = CvBridge()

        # Socket UDP - Timeout de 0.3 para no trabar el flujo
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 9000))
        self.sock.settimeout(0.3)

        # Publicadores
        self.image_pub = self.create_publisher(Image, 'tello_image', 10)
        self.bat_pub = self.create_publisher(String, 'battery_status', 10)
        self.height_pub = self.create_publisher(String, 'height_status', 10)
        self.speed_pub = self.create_publisher(String, 'speed_status', 10)

        # Suscriptor
        self.subscription = self.create_subscription(String, 'tello_cmd', self.command_callback, 10)

        # Iniciar Tello
        self.send_udp_command('command')
        time.sleep(0.2)
        self.send_udp_command('streamon')

        # Hilo de Video
        self.video_thread = threading.Thread(target=self.video_worker, daemon=True)
        self.video_thread.start()

        # Timer para Telemetría cada 2 segundos
        self.create_timer(2.0, self.get_telemetry)
        self.get_logger().info('🚀 Drone Connector iniciado correctamente')

    def send_udp_command(self, command):
        try:
            self.sock.sendto(command.encode('utf-8'), (self.tello_ip, self.tello_port))
        except:
            pass

    def command_callback(self, msg):
        self.send_udp_command(msg.data)

    def get_telemetry(self):
        # Batería
        try:
            self.send_udp_command('battery?')
            data, _ = self.sock.recvfrom(1024)
            self.bat_pub.publish(String(data=data.decode().strip()))
        except:
            pass

        # Altura
        try:
            self.send_udp_command('height?')
            data, _ = self.sock.recvfrom(1024)
            resp = data.decode().strip()
            if "unknown" not in resp.lower():
                self.height_pub.publish(String(data=resp))
            else:
                self.height_pub.publish(String(data="0"))
        except:
            pass

    def video_worker(self):
        addr = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=5000000'
        cap = cv2.VideoCapture(addr, cv2.CAP_FFMPEG)

        while rclpy.ok():
            ret, frame = cap.read()
            if ret:
                msg = self.bridge.cv2_to_imgmsg(frame, 'bgr8')
                self.image_pub.publish(msg)
            else:
                self.send_udp_command('streamon')
                time.sleep(1.0)

def main(args=None):
    rclpy.init(args=args)
    node = DroneConnector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()