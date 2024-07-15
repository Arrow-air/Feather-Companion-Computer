#!/bin/bash

# Pls Navigate to your project directory
cd ..

# Run Backend Data handler
sudo python3 src/FCPC.py

# Run System State Window Frontend
sudo python3 src/display1.py &

# Run System Information Window Frontend
sudo python3 src/display2.py &
