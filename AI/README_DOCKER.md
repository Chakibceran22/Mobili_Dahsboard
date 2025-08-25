# Mobili AI Chatbot Service - Docker Container

An intelligent AI-powered chatbot service that provides data visualization and device management capabilities for the Mobili Dashboard platform.

## 🐳 Container Features

- 🤖 **AI-Powered Chat**: Uses Google Gemini AI for intelligent conversation
- 📊 **Data Visualization**: Automatically generates charts and graphs from IoT device data
- 🔍 **Smart Device Selection**: Intelligently selects devices based on natural language queries
- 📱 **Device Management**: Lists and manages IoT devices from ThingsBoard
- 🎯 **RESTful API**: Easy integration with frontend applications
- 🔒 **Production Ready**: Health checks, logging, and error handling

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google AI API Key
- Running ThingsBoard instance

### 1. Environment Setup

```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your GOOGLE_API_KEY
nano .env
```

### 2. Deploy with Script

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 3. Manual Deployment

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ai-chatbot
```

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8003/health
```

### Chat API
```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me temperature data for the last 7 days"}'
```

### Service Information
```bash
curl http://localhost:8003/
```

### Generated Plots
```bash
curl http://localhost:8003/plots/<filename>
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API Key | **Required** |
| `THINGSBOARD_URL` | ThingsBoard API URL | `http://192.168.0.1:8081` |
| `THINGSBOARD_USERNAME` | ThingsBoard username | `tenant@mobilis.dz` |
| `THINGSBOARD_PASSWORD` | ThingsBoard password | `tenant` |
| `FLASK_ENV` | Flask environment | `production` |

### Docker Compose Override

For custom configurations:

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  ai-chatbot:
    environment:
      - THINGSBOARD_URL=http://your-thingsboard:8080
      - THINGSBOARD_USERNAME=your-username
    ports:
      - "8004:8003"  # Use different port
```

## 🧪 Testing

### Basic Test
```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, are you working?"}'
```

### Pipeline Test
```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me temperature data"}'
```

### Health Test
```bash
curl http://localhost:8003/health | jq
```

## 🔍 Troubleshooting

### Service Not Starting

1. **Check environment variables**:
   ```bash
   docker-compose config
   ```

2. **View detailed logs**:
   ```bash
   docker-compose logs ai-chatbot
   ```

3. **Check container status**:
   ```bash
   docker-compose ps
   ```

### Common Issues

#### "No module named 'flask'"
```bash
# Rebuild the image
docker-compose build --no-cache ai-chatbot
docker-compose up -d
```

#### "Failed to login via list_devices.py"
```bash
# Check ThingsBoard connection
curl http://192.168.0.1:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"tenant@mobilis.dz","password":"tenant"}'
```

#### "GOOGLE_API_KEY not set"
```bash
# Verify environment file
cat .env | grep GOOGLE_API_KEY
```

## 📊 Integration

### With Main ThingsBoard Stack

Add to your main `docker-compose.yml`:

```yaml
services:
  ai-chatbot:
    build:
      context: ./AI
      dockerfile: Dockerfile
    container_name: mobili-ai-chatbot
    ports:
      - "8003:8003"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./AI/plots:/app/plots
    depends_on:
      - thingsboard-ce
    networks:
      - default
```

### Frontend Integration

Update the Angular service to point to the containerized service:

```typescript
// ai-visualizer.service.ts
private readonly API_BASE_URL = 'http://localhost:8003';
```

## 🛠️ Development

### Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment
export GOOGLE_API_KEY="your_key_here"

# Run locally
python chatbot_visualize.py
```

### Custom Image

```bash
# Build custom image
docker build -t your-registry/mobili-ai-chatbot:v1.0 .

# Push to registry
docker push your-registry/mobili-ai-chatbot:v1.0
```

## 📈 Monitoring

### Container Health

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' mobili-ai-chatbot

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' mobili-ai-chatbot
```

### Resource Usage

```bash
# Monitor resources
docker stats mobili-ai-chatbot

# View logs in real-time
docker-compose logs -f ai-chatbot
```

## 🔒 Security

### Production Deployment

1. **Use secrets for API keys**:
   ```yaml
   secrets:
     google_api_key:
       external: true
   ```

2. **Enable SSL/TLS**:
   ```yaml
   environment:
     - FLASK_ENV=production
     - SSL_CERT_PATH=/certs/cert.pem
   ```

3. **Network isolation**:
   ```yaml
   networks:
     internal:
       internal: true
   ```

## 📋 File Structure

```
AI/
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Service orchestration
├── .dockerignore              # Exclude files from build
├── .env.template              # Environment template
├── deploy.sh                  # Deployment script
├── requirements.txt           # Python dependencies
├── README_DOCKER.md           # This file
├── chatbot_visualize.py       # Main Flask application
├── smart_device_selector.py   # AI device selection
├── list_devices.py            # Device listing
├── fetch_battery_data.py      # Data fetching
├── device_pipeline.py         # Data pipeline
└── plots/                     # Generated visualizations
```

## 🆘 Support

- **Logs**: `docker-compose logs -f ai-chatbot`
- **Shell Access**: `docker-compose exec ai-chatbot bash`
- **Restart**: `docker-compose restart ai-chatbot`
- **Clean Rebuild**: `docker-compose build --no-cache && docker-compose up -d`
