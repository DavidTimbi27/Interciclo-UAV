import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import os

class TelemetryMonitor(Node):
    def __init__(self):
        super().__init__('telemetry_monitor')

        # Variables para almacenar el último valor recibido
        self.battery = "Conectando..."
        self.height = "Conectando..."
        self.speed = "Conectando..."

        # Suscriptores a los tópicos definidos en el alcance del proyecto
        self.create_subscription(String, 'battery_status', self.battery_callback, 10)
        self.create_subscription(String, 'height_status', self.height_callback, 10)
        self.create_subscription(String, 'speed_status', self.speed_callback, 10)

        # Timer para actualizar la pantalla cada segundo
        self.timer = self.create_timer(1.0, self.print_dashboard)
        self.get_logger().info('📊 Monitor de Telemetría iniciado. Esperando datos del dron...')

    def battery_callback(self, msg):
        self.battery = msg.data

    def height_callback(self, msg):
        self.height = msg.data

    def speed_callback(self, msg):
        self.speed = msg.data

    def print_dashboard(self):
        # Limpiar la consola para un efecto visual de panel profesional
        print('\033c', end='')

        print("==========================================")
        print("        🛰️  SISTEMA DE TELEMETRÍA UAV        ")
        print("==========================================")
        # Mostrar datos formateados de manera legible
        print(f"  🔋 NIVEL DE BATERÍA :  {self.battery} %")
        print(f"  📏 ALTITUD ACTUAL   :  {self.height} cm")
        print(f"  💨 VELOCIDAD ACTUAL :  {self.speed} cm/s")
        print("==========================================")
        print("  Estado: Recibiendo datos en tiempo real  ")
        print("==========================================")

def main(args=None):
    rclpy.init(args=args)
    node = TelemetryMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()