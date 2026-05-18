import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import os

# Configuraciones para Docker/Windows
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["XDG_RUNTIME_DIR"] = "/tmp"

class VideoViewer(Node):
    def __init__(self):
        super().__init__('video_viewer')
        self.bridge = CvBridge()
        self.received_first_frame = False

        # Publicador para forzar el encendido de la cámara
        self.cmd_pub = self.create_publisher(String, 'tello_cmd', 10)

        # Suscripción al tópico de imagen
        self.subscription = self.create_subscription(
            Image, 'tello_image', self.image_callback, 10)

        # Timer para pedir video cada 2 segundos si no ha llegado nada
        self.timer = self.create_timer(2.0, self.request_video)
        self.get_logger().info('🟢 Visor iniciado. Esperando paquetes en /tello_image...')

    def request_video(self):
        if not self.received_first_frame:
            msg = String()
            msg.data = 'streamon'
            self.cmd_pub.publish(msg)
            self.get_logger().warning('📡 No recibo datos. Re-enviando "streamon" al dron...')

    def image_callback(self, msg):
        if not self.received_first_frame:
            self.get_logger().info('✅ ¡CONEXIÓN ESTABLECIDA! Recibiendo flujo de video.')
            self.received_first_frame = True
            cv2.namedWindow("Vista de Camara Tello", cv2.WINDOW_NORMAL)

        try:
            # Convertir imagen
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

            # MOSTRAR EN VENTANA
            cv2.imshow("Vista de Camara Tello", frame)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Error al procesar frame: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = VideoViewer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main()