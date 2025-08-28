#!/usr/bin/env python3
"""
HTTP Publisher to ThingsBoard
Forwards power data from MQTT topic to ThingsBoard device via HTTP API
"""

import paho.mqtt.client as mqtt
import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SOURCE_MQTT_BROKER = "your_source_broker_host"  # Replace with your MQTT broker
SOURCE_MQTT_PORT = 1883
SOURCE_TOPIC = "N/c0619ab6cfae/battery/256/Dc/0/Power"

THINGSBOARD_HOST = "http://localhost:8081"  # Your ThingsBoard HTTP endpoint
DEVICE_TOKEN = "YOUR_DEVICE_TOKEN"  # Replace with actual device token

class HttpForwarder:
    def __init__(self):
        # Source MQTT client (receives data)
        self.source_client = mqtt.Client("power_receiver_http")
        self.source_client.on_connect = self.on_source_connect
        self.source_client.on_message = self.on_source_message
        
    def on_source_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to source MQTT broker with result code {rc}")
        client.subscribe(SOURCE_TOPIC)
        logger.info(f"Subscribed to topic: {SOURCE_TOPIC}")
        
    def on_source_message(self, client, userdata, msg):
        try:
            # Get the power value
            power_value = float(msg.payload.decode())
            logger.info(f"Received power value: {power_value}")
            
            # Prepare telemetry data for ThingsBoard
            telemetry_data = {
                "power": power_value,
                "timestamp": int(time.time() * 1000)  # ThingsBoard expects milliseconds
            }
            
            # Send to ThingsBoard via HTTP API
            url = f"{THINGSBOARD_HOST}/api/v1/{DEVICE_TOKEN}/telemetry"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=telemetry_data, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Successfully published to ThingsBoard: {telemetry_data}")
            else:
                logger.error(f"Failed to publish to ThingsBoard. Status: {response.status_code}, Response: {response.text}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def start(self):
        try:
            # Connect to source MQTT broker
            self.source_client.connect(SOURCE_MQTT_BROKER, SOURCE_MQTT_PORT, 60)
            self.source_client.loop_start()
            
            logger.info("HTTP forwarder started. Press Ctrl+C to stop.")
            
            # Keep running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping HTTP forwarder...")
            self.source_client.loop_stop()
            self.source_client.disconnect()

if __name__ == "__main__":
    forwarder = HttpForwarder()
    forwarder.start()
