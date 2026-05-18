# Tello UAV ROS2 Control Station and Vision Pipeline

This repository contains a containerized control system and real-time computer vision pipeline for the DJI Tello quadcopter. Built on ROS2 Humble and encapsulated within Docker, the project integrates automated mission planning, multi-class HSV color segmentation, live telemetry rendering, and an asynchronous safety failsafe system.

## Key Features

- **Isolated Docker Environment**: Complete ROS2 Humble Desktop-Full ecosystem containerized with X11 forwarding for native GUI rendering on the host machine.
- **HSV Vision Pipeline**: Real-time concurrent detection, bounding box generation, and counting of targeted chromatic entities (Red and Black objects) using OpenCV.
- **Mission Planner HMI**: A decoupled Tkinter-based Graphical User Interface that queues and transmits sequential SDK commands without blocking the main ROS2 execution threads.
- **Asynchronous Battery Failsafe**: A high-priority safety node that actively monitors telemetry and triggers an automated autonomous landing sequence when battery levels drop to 15% or below.
- **Console Telemetry Dashboard**: Live monitoring of state vectors including altitude, speed, and connectivity status over UDP socket streams.

## System Architecture

The ecosystem relies on decentralized ROS2 nodes communicating over a publisher/subscriber topology:

- `tello_driver` (or custom connector): Manages low-level UDP sockets with the UAV (Video on port 11111, Commands on port 8889).
- `vision_processor`: Subscribes to the camera topic, applies HSV masks, filters image noise, and publishes object coordinate data and counts.
- `battery_failsafe`: Intercepts `/battery_status` strings, running a deterministic conditional routine to enforce flight aborts if thresholds are violated.
- `control_gui`: Provides the human-machine interface for manual overrides and mission loading.

## Prerequisites

- Docker Engine (v24.0 or higher)
- X11 Server installed on the host machine (Native on Linux, VcXsrv/WSL2 on Windows, or XQuartz on macOS)
- Wi-Fi adapter configured to connect to the DJI Tello access point.

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/youruser/tello-ros2-docker.git](https://github.com/youruser/tello-ros2-docker.git)
   cd tello-ros2-docker
