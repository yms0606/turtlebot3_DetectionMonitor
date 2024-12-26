# 🕵️‍♂️ TurtleBot3 Detection and Monitoring System

This repository introduces a cutting-edge surveillance and tracking system using **TurtleBot3**, integrated with **CCTV cameras**, **YOLO object detection**, and **Flask** for a real-time monitoring UI. The system is designed to track and pursue vehicles dynamically, ensuring robust monitoring and security.
<br>
<br>

## 📋 Project Overview

- **CCTV Integration**: Monitors the entire map using real-time camera feeds.
- **YOLO Object Detection**: Detects and tracks vehicles with unique IDs for real-time tracking.
- **Flask UI**: Displays CCTV footage and allows user commands to be sent to the robot.
- **Dynamic Vehicle Tracking**: Converts image coordinates from the CCTV to TurtleBot3’s spatial coordinates and transmits them.
- **Pursuit Algorithm**: Enables TurtleBot3 to chase the tracked vehicle, even during evasion, by continuously updating the tracked ID.
- **Data Storage**: Utilizes SQLite for storing tracking information and generating statistical reports.
- **ROS Communication**: Facilitates seamless communication between components.
<br>
<br>

## 🌟 Key Features

- **Real-Time Surveillance**: 
  View live CCTV footage in a Flask-powered UI.
- **Interactive Tracking**: 
  Input the tracked vehicle’s ID in the UI, and the TurtleBot3 immediately pursues the target.
- **Coordinate Transformation**: 
  Converts camera coordinates into spatial data for TurtleBot3 navigation.
- **SQLite Integration**: 
  Logs tracking data for analysis and reporting.

<img src="https://github.com/user-attachments/assets/b70bba41-a1e2-4246-9b6e-66055ad5addf" width=600>

<br>
<br>

## 📸 Demo Images

<img src="https://github.com/user-attachments/assets/5c283aa6-03ca-4b61-b7a2-c3d1545fa7c3" width=500>
<br>
<img src="https://github.com/user-attachments/assets/ca9bc561-a86a-49b0-9efb-aab081b11618" width=500>

<br>
<br>

## 👨‍💻 Contributors
A big thank you to everyone who made this project possible! 🎉  
Click on the names below to view their GitHub profiles:

- [**MINSIK YOON**](https://github.com/yms0606)   
- [**junha JANG**](https://github.com/zzangzzun)  
- [**seunghwan JEONG**](https://github.com/JSeungHwan)

