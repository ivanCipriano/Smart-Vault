# SmartVault – IoT Security System

## Overview
**SmartVault** is an IoT-based smart security system designed to control access and monitor the status of a secure vault.
The system integrates physical security mechanisms (keypad access, automated lock, and lighting) with an advanced intrusion detection alarm. 

A **Node-RED dashboard** provides real-time monitoring, historical access data visualization, and remote control through MQTT-based communication. The system is designed to ensure strict access control while offering remote management capabilities and push notifications in case of security breaches.

---

## System Interface & Dashboard

Since the system relies heavily on visual feedback, here is an overview of the user interfaces:

### Physical Interface (Vault Screens)
The system features two separate displays for distinct purposes:
- **Access Display (Screen 1):** Acts as the user interaction point. It prompts the user with an "Insert access code" message. As the user types on the numeric keypad, the screen masks the input by displaying asterisks (`*`), mimicking a classic ATM or vault interface.
- **Statistics Display (Screen 2):** Acts as a local monitoring station. It shows real-time data, including:
  - Door status (Open/Closed).
  - Alarm status (Active/Inactive).
  - Visual indicator (a blinking dot) representing an actively ringing alarm.
  - Total number of accesses.

### Node-RED Dashboard
The remote control panel allows the administrator to:
- Remotely open or close the vault door.
- Monitor the real-time status of the door and the alarm.
- Remotely turn off the alarm if triggered.
- View a weekly access graph to track usage patterns over time.

---

## Features
- 🔐 **Access Control**:
  - Secure unlock via a physical numeric keypad.
  - Automatic activation of an internal courtesy light when the vault opens.
  - Remote door control via the Node-RED dashboard.

- 🚨 **Security & Alarm Logic**:
  - The alarm triggers automatically in two cases:
    1. After 3 consecutive incorrect PIN entries.
    2. Forced entry (the vault door opens without the correct PIN being entered) simulated with an IR Sensor.
  - The alarm can be disarmed locally by entering the correct PIN on the keypad, or remotely via the dashboard.
  - Push notifications are sent immediately to the administrator when the alarm triggers.

- 📊 **Monitoring & Visualization**:
  - Dual local screens (Access and Statistics) for on-site monitoring.
  - Node-RED dashboard for remote system management.
  - Weekly access trends visualized on dashboard charts.

---

## Hardware Components
### Inputs & Sensors
- **Numeric Keypad** – For PIN entry.
- **Door Sensor** – To detect forced entry and door status.

### Outputs & Actuators
- **2x Displays (OLED SSD1306)** – One for access interface, one for system stats.
- **Servo Motor** – To control the physical locking mechanism of the vault door.
- **Buzzer** – For the physical intrusion alarm.
- **LED** – Internal vault lighting that turns on upon successful opening.

---

## Software Architecture
- **Firmware (Python for Microcontroller)**:
  - Classes for each component (e.g., `Keypad`, `Display`, `Alarm`, `Door`, `Sensor_HW`) to modularize hardware control.
  - State machine logic to handle the alarm triggers (3 wrong attempts, forced opening).
  - `mqtt` module handles **MQTT communication** (connection, publishing status updates, subscribing to remote commands).

- **Node-RED Dashboard**:
  - Real-time UI displaying MQTT payloads from the microcontroller.
  - Buttons for remote override (Lock/Unlock, Alarm Off).
  - Data aggregation nodes to generate the weekly access charts.
  - Integration with notification nodes to push alerts to the administrator's device.

---

## Protocols & Communication
- **MQTT**: Core protocol for publish/subscribe communication between the physical vault and the Node-RED dashboard.
- **I²C**: Used for communication between the microcontroller and the two displays to minimize wiring.
- **Wi-Fi**: Microcontroller connectivity to reach the MQTT broker.

---

## Repository Structure
```bash
├── /src              # Python source files (Microcontroller firmware)
│   ├── main.py
│   ├── Keypad.py
│   ├── Display.py
│   ├── Alarm.py
│   └── ...
|
├── /dashboard        # Node-RED dashboard flow
│   └── flows gruppo04.json
└── README.md
