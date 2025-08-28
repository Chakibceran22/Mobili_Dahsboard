#!/usr/bin/env python3
"""
MQTT Publisher to ThingsBoard
Forwards power data from your MQTT topic to ThingsBoard device
"""

import paho.mqtt.client as mqtt
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

THINGSBOARD_HOST = "localhost"  # Your ThingsBoard host
THINGSBOARD_PORT = 1884  # MQTT port from your docker-compose (mapped to 1883 internal)
DEVICE_TOKEN = "YOUR_DEVICE_TOKEN"  # Replace with actual device token

class MqttForwarder:
    def __init__(self):
        # Source MQTT client (receives data)
        self.source_client = mqtt.Client("power_receiver")
        self.source_client.on_connect = self.on_source_connect
        self.source_client.on_message = self.on_source_message
        
        # ThingsBoard MQTT client (sends data)
        self.tb_client = mqtt.Client("tb_publisher")
        self.tb_client.username_pw_set(DEVICE_TOKEN)
        self.tb_client.on_connect = self.on_tb_connect
        
    def on_source_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to source MQTT broker with result code {rc}")
        client.subscribe(SOURCE_TOPIC)
        logger.info(f"Subscribed to topic: {SOURCE_TOPIC}")
        
    def on_tb_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to ThingsBoard MQTT with result code {rc}")
        
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
            
            # Publish to ThingsBoard
            tb_topic = "v1/devices/me/telemetry"
            self.tb_client.publish(tb_topic, json.dumps(telemetry_data))
            logger.info(f"Published to ThingsBoard: {telemetry_data}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def start(self):
        try:
            # Connect to source MQTT broker
            self.source_client.connect(SOURCE_MQTT_BROKER, SOURCE_MQTT_PORT, 60)
            
            # Connect to ThingsBoard
            self.tb_client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
            
            # Start both clients
            self.source_client.loop_start()
            self.tb_client.loop_start()
            
            logger.info("MQTT forwarder started. Press Ctrl+C to stop.")
            
            # Keep running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping MQTT forwarder...")
            self.source_client.loop_stop()
            self.tb_client.loop_stop()
            self.source_client.disconnect()
            self.tb_client.disconnect()

if __name__ == "__main__":
    forwarder = MqttForwarder()
    forwarder.start()
