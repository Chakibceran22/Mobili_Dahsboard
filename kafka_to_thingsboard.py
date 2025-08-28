#!/usr/bin/env python3
"""
Kafka to ThingsBoard Bridge
Consumes from Kafka and sends to ThingsBoard via REST API
"""

from kafka import KafkaConsumer
import requests
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'battery-power-data'
THINGSBOARD_URL = 'http://localhost:8081'
DEVICE_TOKEN = 'YOUR_DEVICE_TOKEN'  # Replace with actual device token

class KafkaToThingsBoard:
    def __init__(self):
        self.consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_SERVERS,
            auto_offset_reset='latest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
    def send_to_thingsboard(self, data):
        """Send telemetry data to ThingsBoard via REST API"""
        try:
            # Format data for ThingsBoard
            telemetry = {
                'power': data.get('power'),
                'ts': data.get('timestamp', int(time.time() * 1000))
            }
            
            # Send to ThingsBoard
            url = f"{THINGSBOARD_URL}/api/v1/{DEVICE_TOKEN}/telemetry"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=telemetry, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Successfully sent to ThingsBoard: {telemetry}")
            else:
                logger.error(f"Failed to send to ThingsBoard: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending to ThingsBoard: {e}")
    
    def start_consuming(self):
        """Start consuming from Kafka and forwarding to ThingsBoard"""
        logger.info(f"Starting Kafka consumer for topic: {KAFKA_TOPIC}")
        
        try:
            for message in self.consumer:
                logger.info(f"Received from Kafka: {message.value}")
                self.send_to_thingsboard(message.value)
                
        except KeyboardInterrupt:
            logger.info("Stopping Kafka consumer...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    bridge = KafkaToThingsBoard()
    bridge.start_consuming()
