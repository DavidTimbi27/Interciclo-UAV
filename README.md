# Estación de Control ROS2 y Pipeline de Visión para UAV Tello

Este repositorio contiene un sistema de control contenedorizado y un pipeline de visión artificial en tiempo real para el cuadricóptero DJI Tello. Desarrollado sobre ROS2 Humble y encapsulado en Docker, el proyecto integra la planificación automatizada de misiones, segmentación de color HSV multiclase, renderizado de telemetría en vivo y un sistema asíncrono de seguridad ante fallos (failsafe).

## Características Principales

- **Entorno Docker Aislado**: Ecosistema completo de ROS2 Humble Desktop-Full contenedorizado con redirección X11 para el renderizado nativo de interfaces gráficas en la máquina host.
- **Pipeline de Visión HSV**: Detección concurrente en tiempo real, generación de cuadros delimitadores (bounding boxes) y conteo de entidades cromáticas específicas (objetos rojos y negros) mediante OpenCV.
- **HMI del Planificador de Misiones**: Interfaz gráfica de usuario descentralizada basada en Tkinter que encola y transmite instrucciones secuenciales del SDK sin bloquear los hilos principales de ejecución de ROS2.
- **Failsafe de Batería Asíncrono**: Nodo de seguridad de alta prioridad que monitorea activamente la telemetría y activa una secuencia automatizada de aterrizaje autónomo cuando el nivel de batería es igual o inferior al 15%.
- **Dashboard de Telemetría en Consola**: Monitoreo en tiempo real de los vectores de estado, incluyendo altitud, velocidad y estado de la conectividad a través de flujos de sockets UDP.

## Arquitectura del Sistema

El ecosistema se basa en nodos descentralizados de ROS2 que se comunican mediante una topología de publicador/suscriptor:

- `tello_driver` (o conector personalizado): Gestiona los sockets UDP de bajo nivel con el UAV (Video en el puerto 11111, Comandos en el puerto 8889).
- `vision_processor`: Se suscribe al tópico de la cámara, aplica las máscaras HSV, filtra el ruido de la imagen y publica los datos de conteo y coordenadas de los objetos.
- `battery_failsafe`: Intercepta los strings de `/battery_status`, ejecutando una rutina condicional determinista para forzar el aborto del vuelo si se violan los umbrales de seguridad.
- `control_gui`: Proporciona la interfaz hombre-máquina para anulaciones manuales y carga de misiones.

## Requisitos Previos

- Docker Engine (v24.0 o superior).
- Servidor X11 instalado en la máquina host (Nativo en Linux, VcXsrv/WSL2 en Windows, o XQuartz en macOS).
- Adaptador Wi-Fi configurado para conectarse al punto de acceso del DJI Tello.
