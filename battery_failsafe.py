import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class BatteryFailsafe(Node):
    def __init__(self):
        super().__init__('battery_failsafe')

        # Escucha los datos del nivel de batería
        self.subscription = self.create_subscription(
            String, 'battery_status', self.battery_callback, 10)

        # Publicador para enviar el comando de aterrizaje de emergencia
        self.cmd_pub = self.create_publisher(String, 'tello_cmd', 10)

        # Bandera para no enviar el comando 'land' repetidas veces
        self.emergency_triggered = False

        self.get_logger().info('🛡️ Sistema Failsafe ACTIVADO. Vigilando nivel de batería...')

    def battery_callback(self, msg):
        try:
            # Convertir el mensaje de texto a número entero
            battery_level = int(msg.data)

            # Condición de emergencia: Batería menor a 30%
            if battery_level < 30 and not self.emergency_triggered:
                self.get_logger().error(f'¡PELIGRO! Batería crítica ({battery_level}%). ¡Forzando ATERRIZAJE AUTOMÁTICO!')

                # Crear y enviar mensaje de aterrizaje rápido
                land_msg = String()
                land_msg.data = 'land'
                self.cmd_pub.publish(land_msg)

                self.emergency_triggered = True

            # Si la batería vuelve a subir (por ejemplo, si le pones una pila nueva o en la simulación)
            elif battery_level >= 30 and self.emergency_triggered:
                self.get_logger().info('Nivel de batería seguro restablecido.')
                self.emergency_triggered = False

        except ValueError:
            # Si llega un texto que no es un número (ej. un 'ok'), se ignora
            pass

def main(args=None):
    rclpy.init(args=args)
    node = BatteryFailsafe()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()