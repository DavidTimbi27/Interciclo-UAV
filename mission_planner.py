import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
import threading

class MissionPlanner(Node):
    def __init__(self):
        super().__init__('mission_planner')

        # Publicador que enviará los comandos al tópico que escucha el drone_connector
        self.cmd_pub = self.create_publisher(String, 'tello_cmd', 10)
        self.get_logger().info('Nodo mission_planner iniciado. La misión comenzará en 5 segundos...')

        # Lanzamos la misión en un hilo separado para que ROS siga funcionando y publicando
        self.mission_thread = threading.Thread(target=self.execute_mission, daemon=True)
        self.mission_thread.start()

    def send_command(self, cmd_str):
        msg = String()
        msg.data = cmd_str
        self.cmd_pub.publish(msg)
        self.get_logger().info(f'>> Publicado: {cmd_str}')

    def execute_mission(self):
        # Dar tiempo inicial para asegurar que los otros nodos estén listos
        time.sleep(5.0)

        # 1. Enviar el comando de despegue
        self.get_logger().info('PASO 1: Iniciando despegue')
        self.send_command('takeoff')

        # 2 y 3. Esperar estabilización (Aumentado a 7 segundos)
        self.get_logger().info('PASO 2 y 3: Esperando estabilización en el aire (7 segs)...')
        time.sleep(7.0)

        # 4. Enviar el comando para avanzar 50 cm hacia adelante
        self.get_logger().info('PASO 4: Avanzando 50 cm en el eje X')
        self.send_command('forward 50')

        # 5. Pausar durante un tiempo configurable (Aumentado a 7 segundos)
        self.get_logger().info('PASO 5: Pausa tras el avance (7 segs)...')
        time.sleep(7.0)

        # 6. Enviar comando para retroceder 50 cm (volver a la posición original)
        self.get_logger().info('PASO 6: Retrocediendo 50 cm')
        self.send_command('back 50')

        # 7. Pausar durante un tiempo configurable (Aumentado a 7 segundos)
        self.get_logger().info('PASO 7: Pausa tras el retroceso (7 segs)...')
        time.sleep(7.0)

        # 8. Enviar comando de aterrizaje
        self.get_logger().info('PASO 8: Aterrizando')
        self.send_command('land')

        self.get_logger().info('¡MISIÓN AUTÓNOMA FINALIZADA!')

def main(args=None):
    rclpy.init(args=args)
    node = MissionPlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()