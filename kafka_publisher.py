#!/usr/bin/env python3
"""
Kafka Producer for ThingsBoard
Forwards power data from MQTT to Kafka topic for ThingsBoard consumption
"""

import paho.mqtt.client as mqtt
from kafka import KafkaProducer
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SOURCE_MQTT_BROKER = "localhost"  # Your MQTT broker
SOURCE_MQTT_PORT = 1884
SOURCE_TOPIC = "N/c0619ab6cfae/battery/256/Dc/0/Power"

KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']  # Your Kafka broker
KAFKA_TOPIC = "tb_rule_engine.main"  # ThingsBoard's main topic
DEVICE_ID = "YOUR_DEVICE_ID"  # Replace with actual device ID from ThingsBoard

class KafkaForwarder:
    def __init__(self):
        # MQTT client (receives data)
        self.mqtt_client = mqtt.Client("kafka_forwarder")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        # Kafka producer
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
    def on_mqtt_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to MQTT broker with result code {rc}")
        client.subscribe(SOURCE_TOPIC)
        logger.info(f"Subscribed to topic: {SOURCE_TOPIC}")
        
    def on_mqtt_message(self, client, userdata, msg):
        try:
            # Get the power value
            power_value = float(msg.payload.decode())
            logger.info(f"Received power value: {power_value}")
            
            # Create ThingsBoard message format
            tb_message = {
                "deviceId": DEVICE_ID,
                "deviceType": "default",
                "ts": int(time.time() * 1000),  # Timestamp in milliseconds
                "values": {
                    "power": power_value
                }
            }
            
            # Send to Kafka
            future = self.kafka_producer.send(
                KAFKA_TOPIC, 
                value=tb_message,
                key=DEVICE_ID
            )
            
            # Wait for confirmation
            record_metadata = future.get(timeout=10)
            logger.info(f"Message sent to Kafka topic {record_metadata.topic} "
                       f"partition {record_metadata.partition} "
                       f"offset {record_metadata.offset}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def start(self):
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(SOURCE_MQTT_BROKER, SOURCE_MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            
            logger.info("Kafka forwarder started. Press Ctrl+C to stop.")
            
            # Keep running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping Kafka forwarder...")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.kafka_producer.close()

if __name__ == "__main__":
    forwarder = KafkaForwarder()
    forwarder.start()
