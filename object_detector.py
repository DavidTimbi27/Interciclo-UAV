import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32
from cv_bridge import CvBridge
import cv2
import numpy as np
import os

# Configuración para visualización en Docker (según recomendaciones del PDF)
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["XDG_RUNTIME_DIR"] = "/tmp"

class ObjectDetector(Node):
    def __init__(self):
        super().__init__('object_detector')
        self.bridge = CvBridge()

        # Suscripción al tópico de video del dron
        self.subscription = self.create_subscription(
            Image, 'tello_image', self.image_callback, 10)

        # Publicador del conteo total (Tipo Int32 requerido)
        self.count_pub = self.create_publisher(Int32, 'object_count', 10)

        self.get_logger().info('🤖 Nodo IA iniciado: Detectando objetos Rojos y Negros...')

    def image_callback(self, msg):
        try:
            # Convertir imagen ROS a OpenCV
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

            # PASO: Convertir a espacio HSV (más robusto para colores)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # --- DETECCIÓN DE ROJO ---
            # El rojo está en los extremos del espectro HSV
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])
            mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)

            # --- DETECCIÓN DE NEGRO ---
            # El negro se define por una saturación baja y valor (brillo) muy bajo
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([180, 255, 40])
            mask_black = cv2.inRange(hsv, lower_black, upper_black)

            # Contadores individuales
            red_count = 0
            black_count = 0

            # Procesar contornos rojos
            cnts_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts_red:
                if cv2.contourArea(c) > 1500: # Filtro de área para evitar ruido
                    red_count += 1
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, "Rojo", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Procesar contornos negros
            cnts_black, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts_black:
                if cv2.contourArea(c) > 1500:
                    black_count += 1
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 50), 2)
                    cv2.putText(frame, "Negro", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 50), 2)

            # Mostrar resultados en pantalla
            total = red_count + black_count
            cv2.putText(frame, f"Rojos: {red_count} | Negros: {black_count}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Total: {total}", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Publicar el total al tópico ROS2
            msg_total = Int32()
            msg_total.data = total
            self.count_pub.publish(msg_total)

            # Abrir ventana de video
            cv2.imshow("IA: Detector de Objetos Tello", frame)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Error en el procesamiento: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main()