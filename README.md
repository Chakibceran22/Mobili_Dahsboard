# ThingsBoard Custom UI

A modified version of ThingsBoard with enhanced user interface components.

## 📋 Maven Commands Reference

### Essential Build Commands

Based on the project configuration, here are the exact commands to use:

```bash
# 1. Build the complete project
mvn clean install -DskipTests

# 2. Build Docker image (from msa/tb-node directory)
cd msa/tb-node

# For Linux/MacOS:
mvn dockerfile:build@build-docker-image -DskipTests -Ddockerfile.skip=false

# For Windows:
mvn dockerfile:build@build-docker-image -DskipTests "-Ddockerfile.skip=false"
```

### Complete Build Workflow

**For Linux/MacOS:**
```bash
# Step 1: Clone the repository
git clone https://github.com/Chakibceran22/Mobilis_Dashboard.git
cd Mobilis_Dashboard

# Step 2: Build the entire project
mvn clean install -DskipTests

# Step 3: Build Docker image
cd msa/tb-node
mvn dockerfile:build@build-docker-image -DskipTests -Ddockerfile.skip=false

# Step 4: Initialize database (first time only)
docker compose run --rm -e INSTALL_TB=true -e LOAD_DEMO=true thingsboard-ce

# Step 5: Start services
docker compose up -d
```

**For Windows:**
```bash
# Step 1: Configure Git line endings (IMPORTANT - do this first!)
git config --global core.autocrlf input

# Step 2: Clone the repository
git clone https://github.com/Chakibceran22/Mobilis_Dashboard.git
cd Mobilis_Dashboard

# Step 3: Build the entire project
mvn clean install -DskipTests

# Step 4: Build Docker image
cd msa/tb-node
mvn dockerfile:build@build-docker-image -DskipTests "-Ddockerfile.skip=false"

# Step 5: Initialize database (first time only)
docker compose run --rm -e INSTALL_TB=true -e LOAD_DEMO=true thingsboard-ce

# Step 6: Start services
docker compose up -d
```

### Command Explanations

- **`mvn clean install -DskipTests`** - Builds the entire project, skipping tests for faster compilation
- **`mvn dockerfile:build@build-docker-image`** - Executes the specific Docker build execution defined in pom.xml
- **`-DskipTests`** - Skips running unit tests during build
- **`-Ddockerfile.skip=false`** - Enables Docker image building (quoted for Windows shell compatibility)
- **`@build-docker-image`** - Specific execution ID configured in the project's Maven configuration
- **Quotes on Windows** - Windows command prompt requires quotes around parameters with special characters

## 🚀 Quick Start

### Prerequisites

- Java 11+
- Maven 3.6+
- Docker & Docker Compose
- Git

### Windows Users - Important Setup

**⚠️ NOTE: Building Docker image on Windows machine**

To build Docker image, certain scripts, configuration files and sources that will be a part of the Docker image must have **LF** line endings. So before cloning the repo set to *input* the Git **core.autocrlf** configuration option.

For example, to set *core.autocrlf* globally:
```bash
git config --global core.autocrlf input
```

**Then clone the repository after setting this configuration.**

### 1. Clone the Repository

```bash
git clone https://github.com/Chakibceran22/Mobilis_Dashboard.git
cd Mobilis_Dashboard
```

### 2. Build the Project

```bash
mvn clean install -DskipTests
```

This command will:
- Clean previous builds
- Compile all modules
- Install artifacts to local repository
- Skip running tests for faster build

## 🐳 Docker Images

### Available Images

All Docker images can be found in the `msa/` folder. Each microservice has its own Docker configuration:

- **msa/tb-node/** - Main ThingsBoard node (recommended)
- **msa/js-executor/** - JavaScript executor service  
- **msa/web-ui/** - Web UI service
- **msa/transport/** - Transport services (MQTT, HTTP, CoAP)

### Recommended Image: tb-node

**tb-node** is the best image for most deployments as it provides:
- ✅ Spring Boot backend
- ✅ UI components
- ✅ JavaScript executors
- ✅ Complete ThingsBoard functionality

### Building Docker Images

#### Step-by-Step Process:

1. **First, build the entire project:**
   ```bash
   mvn clean install -DskipTests
   ```

2. **Navigate to the tb-node directory:**
   ```bash
   cd msa/tb-node
   ```

3. **Build the Docker image:**

   **For Linux/MacOS:**
   ```bash
   mvn dockerfile:build@build-docker-image -DskipTests -Ddockerfile.skip=false
   ```

   **For Windows:**
   ```bash
   mvn dockerfile:build@build-docker-image -DskipTests "-Ddockerfile.skip=false"
   ```

This command will:
- Execute the specific `build-docker-image` execution ID from the pom.xml
- Build the Docker image with all necessary components
- Skip tests during the Docker build process
- Enable Docker image creation (dockerfile.skip=false)

## 🗄️ Database Setup with PostgreSQL

### Using Docker Compose

This project includes Docker Compose configuration for easy PostgreSQL integration.

### First Time Setup

**⚠️ Run this command ONLY on the first deployment** to install the database schema:

```bash
docker compose run --rm -e INSTALL_TB=true -e LOAD_DEMO=true thingsboard-ce
```

**What this command does:**
- `INSTALL_TB=true` - Installs the core database schema and system resources (widgets, images, rule chains, etc.)
- `LOAD_DEMO=true` - Loads sample tenant account, dashboards and devices for evaluation and testing
- `--rm` - Removes the container after execution to save disk space

**Alternative commands for different scenarios:**
```bash
# Install schema only (without demo data)
docker compose run --rm -e INSTALL_TB=true thingsboard-ce

# For upgrades (when updating ThingsBoard version)
docker compose run --rm -e UPGRADE_TB=true thingsboard-ce
```

### Regular Startup

After the initial setup, start the services with:

```bash
docker compose up -d
```

## 📁 Project Structure

```
.
├── msa/                    # Microservices Docker configurations
│   ├── tb-node/           # Main ThingsBoard node (recommended)
│   ├── tb-web-ui/         # Web UI service
│   ├── tb-js-executor/    # JavaScript executor service
│   └── ...                # Other microservices
├── docker-compose.yml     # Docker Compose configuration
├── pom.xml               # Maven configuration
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables for deployment:

- `INSTALL_TB` - Set to `true` for initial database setup
- `LOAD_DEMO` - Set to `true` to load demo data
- `TB_HOST` - ThingsBoard host URL
- `POSTGRES_DB` - PostgreSQL database name
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password

### Database Configuration

The PostgreSQL configuration is handled through Docker Compose. Modify `docker-compose.yml` to adjust database settings.

## 🛠️ Development

### Building Specific Modules

For this project, follow these specific steps:

```bash
# 1. Build the complete project first
mvn clean install -DskipTests

# 2. Build tb-node Docker image
cd msa/tb-node

# For Linux/MacOS:
mvn dockerfile:build@build-docker-image -DskipTests -Ddockerfile.skip=false

# For Windows:
mvn dockerfile:build@build-docker-image -DskipTests "-Ddockerfile.skip=false"
```

### Development Workflow

After making code changes:

1. **Rebuild the project:**
   ```bash
   mvn clean install -DskipTests
   ```

2. **Rebuild Docker image:**
   ```bash
   cd msa/tb-node
   
   # For Linux/MacOS:
   mvn dockerfile:build@build-docker-image -DskipTests -Ddockerfile.skip=false
   
   # For Windows:
   mvn dockerfile:build@build-docker-image -DskipTests "-Ddockerfile.skip=false"
   ```

3. **Restart containers:**
   ```bash
   docker compose down
   docker compose up -d
   ```

### Custom UI Development

The UI modifications are integrated into the build process. After making UI changes, follow the development workflow above to see your changes reflected in the running application.

### Debugging Build Issues

If you encounter build issues:

```bash
# Clean everything and rebuild
mvn clean
mvn clean install -DskipTests

# For verbose output during Docker build (Linux/MacOS):
cd msa/tb-node
mvn dockerfile:build@build-docker-image -DskipTests -Ddockerfile.skip=false -X

# For verbose output during Docker build (Windows):
cd msa/tb-node
mvn dockerfile:build@build-docker-image -DskipTests "-Ddockerfile.skip=false" -X
```

## 📊 Usage

### Accessing ThingsBoard

After successful deployment:

- **Web UI:** http://localhost:8080
- **Default Credentials:**
  - **System Admin:** sysadmin@thingsboard.org / sysadmin
  - **Tenant Admin:** tenant@thingsboard.org / tenant

### API Access

- **REST API:** http://localhost:8080/api
- **WebSocket:** ws://localhost:8080/api/ws

## 🐛 Troubleshooting

### Common Issues

1. **Maven Build Issues**
   ```bash
   # If you get "dockerfile.skip=false" errors
   # Make sure Docker is running and accessible
   docker --version
   
   # Clean Maven cache and rebuild
   mvn clean
   mvn install -DskipTests
   
   # For Docker permission issues on Linux
   sudo usermod -aG docker $USER
   # Then logout and login again
   ```

2. **Docker Build Failures**
   ```bash
   # Check Docker daemon status
   sudo systemctl status docker
   
   # Restart Docker service
   sudo systemctl restart docker
   
   # Clean Docker cache
   docker system prune -a
   ```

3. **Database Connection Issues**
   ```bash
   # Check if PostgreSQL container is running
   docker compose logs postgres
   
   # Restart database container
   docker compose restart postgres
   ```

4. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep 8080
   
   # Kill process using port 8080
   sudo kill -9 $(lsof -t -i:8080)
   ```

5. **Windows Line Ending Issues**
   ```bash
   # If you get line ending errors during Docker build
   # Make sure you configured Git BEFORE cloning (see Prerequisites section)
   git config --global core.autocrlf input
   
   # Then re-clone the repository
   rm -rf Mobilis_Dashboard
   git clone https://github.com/Chakibceran22/Mobilis_Dashboard.git
   ```

### Build-Specific Troubleshooting

**If the main build fails:**
```bash
# Clean and rebuild
mvn clean
mvn clean install -DskipTests
```

**If Docker build fails:**
```bash
# Make sure you're in the correct directory
cd msa/tb-node

# Check if Dockerfile exists
ls -la Dockerfile

# Try building with verbose output (Linux/MacOS):
mvn dockerfile:build@build-docker-image -DskipTests -Ddockerfile.skip=false -X

# Try building with verbose output (Windows):
mvn dockerfile:build@build-docker-image -DskipTests "-Ddockerfile.skip=false" -X
```

**If you get execution ID errors:**
```bash
# The @build-docker-image execution ID is specific to this project
# Make sure you're using the exact command for your OS:

# Linux/MacOS:
mvn dockerfile:build@build-docker-image -DskipTests -Ddockerfile.skip=false

# Windows:
mvn dockerfile:build@build-docker-image -DskipTests "-Ddockerfile.skip=false"
```

**Windows-specific issues:**
```bash
# If you get line ending errors, make sure you configured Git before cloning:
git config --global core.autocrlf input

# Then re-clone the repository
git clone https://github.com/Chakibceran22/Mobilis_Dashboard.git
```

### Logs

View application logs:
```bash
# All services
docker compose logs

# Specific service
docker compose logs thingsboard-ce

# Follow logs
docker compose logs -f
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project maintains the same license as the original ThingsBoard project.

## 🔗 Links

- [Original ThingsBoard](https://thingsboard.io/)
- [ThingsBoard Documentation](https://thingsboard.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Note:** This is a modified version of ThingsBoard with custom UI enhancements. For original ThingsBoard documentation, visit the official website.