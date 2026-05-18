import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image as PILImage, ImageTk
import threading
import time

class MissionControlAI(Node):
    def __init__(self):
        super().__init__('mission_control_ai')
        self.bridge = CvBridge()
        self.create_subscription(Image, 'tello_image', self.callback_imagen, 10)
        self.pub_comando = self.create_publisher(String, 'tello_cmd', 10)

        self.mision_en_curso = False
        self.debe_restablecer_ui = False

        # --- CONFIGURACIÓN DE COLORES ---
        self.color_fondo = "#121212"      # Fondo principal
        self.color_tarjeta = "#1e1e1e"    # Fondo de tarjetas
        self.color_acento = "#00adb5"     # Cyan moderno
        self.color_texto = "#eeeeee"      # Blanco suave
        self.color_rojo = "#ff4b2b"       # Rojo neón
        self.color_negro = "#888888"      # Gris para representar negro

        # --- INTERFAZ PRINCIPAL ---
        self.root = tk.Tk()
        self.root.title("ESTACIÓN DE CONTROL TELLO v2.0")
        self.root.configure(bg=self.color_fondo)
        self.root.geometry("1100x600")

        # Fuentes
        self.fuente_titulo = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.fuente_stats = tkFont.Font(family="Courier", size=24, weight="bold")

        # Lado Izquierdo: Video
        self.frame_video = tk.Frame(self.root, bg=self.color_acento, padx=2, pady=2)
        self.frame_video.pack(side=tk.LEFT, padx=20, pady=20)

        self.label_video = tk.Label(self.frame_video, bg="black")
        self.label_video.pack()

        # Lado Derecho: Controles
        self.sidebar = tk.Frame(self.root, bg=self.color_fondo)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20)

        # Planificador de Ruta
        tk.Label(self.sidebar, text="PLANIFICADOR DE MISIÓN", bg=self.color_fondo,
                 fg=self.color_acento, font=self.fuente_titulo).pack(anchor="w", pady=(20,5))

        self.texto_ruta = tk.Text(self.sidebar, width=30, height=8, bg=self.color_tarjeta,
                                  fg=self.color_texto, insertbackground="white",
                                  font=("Consolas", 11), bd=0, padx=10, pady=10)
        self.texto_ruta.pack(fill=tk.X)
        self.texto_ruta.insert(tk.END, "takeoff\nup 40\nforward 50\nland")

        # Botón de Inicio
        self.btn_iniciar = tk.Button(self.sidebar, text="INICIAR MISIÓN", bg=self.color_acento,
                                     fg="white", font=("Helvetica", 12, "bold"), bd=0,
                                     height=2, cursor="hand2", activebackground="#007d82",
                                     command=self.preparar_mision)
        self.btn_iniciar.pack(fill=tk.X, pady=20)

        # Panel de Telemetría (Contadores)
        self.frame_stats = tk.Frame(self.sidebar, bg=self.color_fondo)
        self.frame_stats.pack(fill=tk.X)

        # Creación de tarjetas de estadísticas
        self.crear_tarjeta_stat("OBJETOS ROJOS", self.color_rojo, "val_rojo")
        self.crear_tarjeta_stat("OBJETOS NEGROS", self.color_negro, "val_negro")
        self.crear_tarjeta_stat("TOTAL DETECTADOS", self.color_acento, "val_total")

        self.verificar_estado_mision()

    def crear_tarjeta_stat(self, etiqueta, color, nombre_attr):
        f = tk.Frame(self.frame_stats, bg=self.color_tarjeta, pady=10, bd=1,
                     highlightbackground="#333333", highlightthickness=1)
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text=etiqueta, bg=self.color_tarjeta, fg=color,
                 font=("Helvetica", 9, "bold")).pack()
        lbl = tk.Label(f, text="0", bg=self.color_tarjeta, fg=self.color_texto,
                       font=self.fuente_stats)
        lbl.pack()
        setattr(self, nombre_attr, lbl)

    def callback_imagen(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Máscaras de color
            m_roja = cv2.inRange(hsv, np.array([0,120,70]), np.array([10,255,255])) + \
                     cv2.inRange(hsv, np.array([170,120,70]), np.array([180,255,255]))
            m_negra = cv2.inRange(hsv, np.array([0,0,0]), np.array([180,255,40]))

            c_rojo = self.procesar_contornos(frame, m_roja, (0, 0, 255))
            c_negro = self.procesar_contornos(frame, m_negra, (255, 0, 0)) # Azul para resaltar

            # Actualizar Imagen
            cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PILImage.fromarray(cv2_img).resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.label_video.imgtk = imgtk
            self.label_video.configure(image=imgtk)

            # Actualizar Etiquetas
            self.val_rojo.config(text=str(c_rojo))
            self.val_negro.config(text=str(c_negro))
            self.val_total.config(text=str(c_rojo + c_negro))
        except: pass

    def procesar_contornos(self, frame, mascara, color_borde):
        cnts, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contador = 0
        for c in cnts:
            if cv2.contourArea(c) > 1500:
                contador += 1
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x,y), (x+w,y+h), color_borde, 3)
        return contador

    def verificar_estado_mision(self):
        if self.debe_restablecer_ui:
            self.mision_en_curso = False
            self.btn_iniciar.config(state=tk.NORMAL, bg=self.color_acento, text="INICIAR MISIÓN")
            self.debe_restablecer_ui = False
        self.root.after(100, self.verificar_estado_mision)

    def preparar_mision(self):
        if not self.mision_en_curso:
            self.mision_en_curso = True
            self.debe_restablecer_ui = False
            self.btn_iniciar.config(state=tk.DISABLED, bg="#444444", text="EJECUTANDO...")

            raw_text = self.texto_ruta.get("1.0", tk.END)
            comandos = [c.strip() for c in raw_text.split('\n') if c.strip()]

            hilo = threading.Thread(target=self.ejecutar_mision, args=(comandos,))
            hilo.daemon = True
            hilo.start()

    def ejecutar_mision(self, comandos):
        for cmd in comandos:
            self.get_logger().info(f"Comando enviado: {cmd}")
            msg = String()
            msg.data = cmd
            self.pub_comando.publish(msg)
            time.sleep(4.0)
        self.debe_restablecer_ui = True

def main(args=None):
    rclpy.init(args=args)
    node = MissionControlAI()
    while rclpy.ok():
        node.root.update_idletasks()
        node.root.update()
        rclpy.spin_once(node, timeout_sec=0.01)
    rclpy.shutdown()

if __name__ == '__main__':
    main()