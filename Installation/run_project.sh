#!/bin/bash

# Pls Navigate to your project directory
cd //home/alexdada/Feather-Companion-Computer/

# Run Backend Data handler
sudo python3 FCPC.py

# Run System State Window Frontend
sudo python3 display1.py &

# Run System Information Window Frontend
sudo python3 display2.py &
