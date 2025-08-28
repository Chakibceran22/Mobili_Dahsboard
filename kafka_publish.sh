#!/bin/bash
# Direct Kafka Publishing Script
# This script sends a power value directly to Kafka for ThingsBoard

KAFKA_CONTAINER="thingsboard_kafka"
KAFKA_TOPIC="tb_rule_engine.mqtt.telemetry"
DEVICE_ID="0I1pmApmNfD9AXeGApHz"
POWER_VALUE="$1"  # Pass power value as first argument

if [ -z "$POWER_VALUE" ]; then
    echo "Usage: $0 <power_value>"
    echo "Example: $0 150.5"
    exit 1
fi

# Create ThingsBoard message
TB_MESSAGE=$(cat <<EOF
{
    "deviceId": "$DEVICE_ID",
    "deviceType": "default",
    "ts": $(date +%s000),
    "values": {
        "power": $POWER_VALUE
    }
}
EOF
)

# Send to Kafka
echo "$TB_MESSAGE" | docker exec -i $KAFKA_CONTAINER kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic $KAFKA_TOPIC \
    --property "key.separator=:" \
    --property "parse.key=true" \
    --property "key.serializer=org.apache.kafka.common.serialization.StringSerializer" \
    --property "value.serializer=org.apache.kafka.common.serialization.StringSerializer"

echo "Sent power value $POWER_VALUE to ThingsBoard via Kafka"
