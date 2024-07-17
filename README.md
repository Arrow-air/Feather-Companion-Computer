
# Feather Flight Companion Computer

## Ground Control Station & Onboard Flight UI

### Functions:
1. Data Logger
2. Telemetry Server
3. User Interface Engine

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [File Descriptions](#file-descriptions)
    - [FCPC.py](#fcpcpy)
    - [Data.py](#datapy)
    - [Veronte.py](#verontepy)
    - [BMS.py](#bmspy)
    - [VESCCAN.py](#vesccanpy)
    - [ESC.py](#escpy)
    - [CyphalCAN3.py](#cyphalcan3py)
    - [TCP.py](#tcppy)
    - [server.py](#serverpy)
    - [protocols_functions.py](#protocols_functionspy)
    - [display1.py](#display1py)
    - [display2.py](#display2py)
    - [Joystick.py](#joystickpy)
    - [LoRa.py](#lorapy)
    - [IO.py](#iopy)

## Introduction

The Flight Companion Computer system designed for both Ground Control Station (GCS) and onboard flight use (FUI). It integrates multiple functionalities including data logging, telemetry server, and a user interface engine. The system is modular, allowing for easy expansion and maintenance, and is designed to provide a robust Data interface for flight operations.

## Architecture Overview

The system is structured into multiple modules, each handling a specific aspect of the overall functionality. These modules include communication protocols, data handling, user interfaces, and specific hardware controls. The main control program loop resides in the `FCPC.py` file.

## File Descriptions

### FCPC.py
**Main Function and Control Logic**  
The central script that coordinates the activities of all other modules. Handles high-level decision making and ensures smooth operation of the entire system.

### Data.py
**Data Handling Module**  
Manages data storage and retrieval within the system. Provides functions for logging data, managing data formats, packaging data to be sent as telemetry.

### Veronte.py
**Veronte Module**  
Interfaces with the main Flight Controller, the Embention Veronte X1, over UART serial. packages flight sensor data, such as attitude and altitude etc.

### BMS.py
**Battery Management System (BMS) Module**  
Packages data from each of the 6 Ennoid X-LITE-V4 BMSs on board the aircraft, including voltage, current, temperature, and state of charge, etc.

### VESCCAN.py
**VESC-CAN Module**  
Interfaces with the VESC CAN bus protocol for interacting with data emminating from the Ennoid X-LITE-V4 BMSs, as implemented by Ennoid.

### ESC.py
**Electronic Speed Controller (ESC) Module**  
Packages data from each of the 6 Mad Motors ECSs on board the aircraft, including voltage, current, temperature, and state of charge, etc.

### CyphalCAN3.py
**Cyphal-CAN Protocol Module**  
Interfaces with the Cyphal-CAN CAN bus protocol for interacting with data emminating from the MAD Motors ECS, as implemented by MAD Motors.

### TCP.py
**TCP/IP Communication Module**  
Implements communication over TCP/IP, handling socket connections, data transmission, and reception over local network, send telemetry data to the displays.

### server.py
**Server Module**  
Sets up a network connection to `display1.py` and `display2.py` to send telementry data to the display screens

### protocols_functions.py
**Protocols Utility Functions Module**  
Contains utility functions used by `server.py`, `display1.py`, and `display2.py`. Provides common functionalities such as message parsing, checksum calculation, and other specific operations.

### display1.py
**Display Module 1**  
Responsible for rendering the "System State Window", primarily displaying data from the Flight Controller.

### display2.py
**Display Module 2**  
Responsible for rendering the "System Infromation Window", primarily displaying data from all the ESCs and BMSs.

### Joystick.py
**Joystick Input Module**  
Handles input from but Logitec USB and Otto CAN joystick devices. Reads joystick movements and button presses, translating their commands to the control system.

### LoRa.py
**Long Range Radio Communication Module**  
Implements communication over the LoRa protocol for long-range, low-power wireless communication. Handles message encoding, decoding, and transmission.

### IO.py
**Input-Output Module**  
Manages I/O on the RPI GPIO pins.

---

This README provides a comprehensive overview of the Project Feather system and its components. For detailed usage and additional information, refer to the documentation within each module and the main `FCPC.py` script, as well as the following reference documents:

## FCPC Concept Document 

[FCPC Concept]( https://docs.google.com/document/d/15r7cTYvV1hOLt8er7vyQtWU0twEOfAIIOQ0pdE-wRtA/edit?pli=1#heading=h.xr0raokzut1w )

## Project Feather Data Network & Ground Equipment Document

[Data Network & Ground Equipment]( https://docs.google.com/document/d/11VlSYsE245VFLZsYB7TvqWuuJ1UnPRjPKnnLWUzqcEM/edit )