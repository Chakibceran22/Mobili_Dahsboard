#!/usr/bin/env python3
"""
Simple Chatbot with GenAI
=========================

A minimal chatbot that uses Google Generative AI to respond to prompts.
Runs on port 8003 and accepts POST requests with prompts.
"""

import os
import json
import subprocess
import re
import sys
import glob
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our smart device selector
try:
    from smart_device_selector import smart_device_selection
    print("✅ Smart device selector imported successfully")
except ImportError as e:
    print(f"⚠️  Could not import smart device selector: {e}")
    smart_device_selection = None

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow requests from ThingsBoard UI
# More permissive CORS configuration for development
CORS(app,
     origins=["*"],  # Allow all origins for now
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
     allow_headers=["*"],  # Allow all headers
     supports_credentials=True)

# Additional manual CORS headers as backup
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Configure Gemini API
# You need to set your API key as an environment variable
# export GOOGLE_API_KEY="your_api_key_here"
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set")
        print("   Set it with: export GOOGLE_API_KEY='your_api_key_here'")
    else:
        genai.configure(api_key=api_key)
        print("✅ Google Generative AI configured successfully")
except Exception as e:
    print(f"❌ Error configuring Google Generative AI: {e}")

# Initialize the model
try:
    # Use Gemini Flash model (fastest and most reliable)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
    print("✅ models/gemini-1.5-flash model loaded successfully")
except Exception as e:
    print(f"❌ Error loading Gemini Flash model: {e}")
    model = None

def is_pipeline_request(prompt):
    """
    Use AI model to intelligently determine if user wants to run the device pipeline
    """
    if not model:
        # Fallback: more comprehensive keyword check if model not available
        keywords = ['pipeline', 'run', 'execute', 'fetch', 'data', 'plot', 'chart', 'show', 'display',
                   'battery', 'temperature', 'humidity', 'visualize', 'graph', 'create']
        return any(word in prompt.lower() for word in keywords)
    
    try:
        analysis_prompt = f"""
You are an intelligent assistant that determines if a user wants to execute a device data pipeline.

The device pipeline:
- Fetches telemetry data from IoT devices
- Creates charts and visualizations
- Handles data like battery level, temperature, humidity
- Generates line charts or bar charts
- Can fetch data for specific time periods

User prompt: "{prompt}"

Respond with ONLY "YES" if the user wants to execute the device pipeline, or "NO" if they want something else.

Examples that should return YES:
- "Run the device pipeline" → YES
- "Fetch battery data" → YES
- "Create a chart of temperature data" → YES
- "Show me device telemetry" → YES
- "Plot the battery for the last day" → YES
- "Show me temperature" → YES
- "Display humidity data" → YES
- "Graph the battery levels" → YES
- "Visualize sensor data" → YES
- "Get device data" → YES
- "Chart the temperature readings" → YES
- "Plot sensor values" → YES

Examples that should return NO:
- "Hello how are you" → NO
- "What's the weather" → NO
- "Tell me a joke" → NO
- "What time is it" → NO
- "How do I configure ThingsBoard" → NO

Response:"""

        response = model.generate_content(analysis_prompt)
        decision = response.text.strip().upper()
        
        print(f"🤖 AI Decision: {decision} for prompt: '{prompt[:50]}...'")
        
        return decision == "YES"
        
    except Exception as e:
        print(f"❌ Error in AI pipeline detection: {e}")
        # Fallback to comprehensive keyword check
        keywords = ['pipeline', 'run', 'execute', 'fetch', 'data', 'plot', 'chart', 'show', 'display',
                   'battery', 'temperature', 'humidity', 'visualize', 'graph', 'create']
        return any(word in prompt.lower() for word in keywords)

def format_time_range_for_display(time_range):
    """Format time range for display in chatbot"""
    if not time_range:
        return "Not specified"

    if time_range.get('hours_back'):
        return f"Last {time_range['hours_back']} hour(s)"
    elif time_range.get('days_back'):
        return f"Last {time_range['days_back']} day(s)"
    elif time_range.get('specific_day_offset') is not None:
        offset = time_range['specific_day_offset']
        start_hour = time_range.get('start_hour', 0)
        end_hour = time_range.get('end_hour', 23)

        if offset == 0:
            day_desc = "Today"
        elif offset == 1:
            day_desc = "Yesterday"
        else:
            day_desc = f"{offset} days ago"

        if start_hour != 0 or end_hour != 23:
            return f"{day_desc} from {start_hour:02d}:00 to {end_hour:02d}:59"
        else:
            return day_desc

    return "Custom range"

def extract_pipeline_params(prompt):
    """
    Use smart device selector to intelligently choose device and parameters
    """
    print("🧠 Using smart device selection...")

    # Try to use smart device selection if available
    if smart_device_selection:
        try:
            selection = smart_device_selection(prompt)
            if selection:
                # Convert smart selector output to pipeline parameters
                # Ensure we capture all available parameters from smart selector
                params = {
                    'device_id': selection['device_id'],
                    'keys': selection['keys'],
                    'chart_type': selection.get('chart_type', 'line')  # Default to line if not specified
                }

                # Handle time range parameters (new format)
                if selection.get('time_range'):
                    params['time_range'] = selection['time_range']
                elif selection.get('days_back'):
                    # Convert legacy days_back to new format for backward compatibility
                    params['time_range'] = {'days_back': selection['days_back']}

                # Store additional metadata for better logging and debugging (separate from pipeline params)
                metadata = {
                    'device_name': selection.get('device_name', 'Unknown Device'),
                    'confidence': selection.get('confidence', 'medium')
                }

                # Combine params with metadata for return (but keep pipeline params clean)
                full_params = {**params, **metadata}

                print(f"📋 Extracted parameters from smart selector:")
                print(f"   🆔 Device ID: {params['device_id']}")
                print(f"   📱 Device Name: {metadata['device_name']}")
                print(f"   🔑 Keys: {params['keys']}")
                print(f"   📊 Chart Type: {params['chart_type']}")
                if params.get('days_back'):
                    print(f"   📅 Days Back: {params['days_back']}")
                print(f"   🎯 Confidence: {metadata['confidence']}")

                print(f"✅ Smart selection successful: {selection['device_name']}")
                return full_params
            else:
                print("⚠️  Smart selection failed, using fallback")
        except Exception as e:
            print(f"❌ Error in smart device selection: {e}")
            print("⚠️  Using fallback parameter extraction")
    
    # Fallback: Use AI for basic parameter extraction
    if not model:
        # Simple regex fallback
        params = {}
        prompt_lower = prompt.lower()
        
        if 'bar' in prompt_lower:
            params['chart_type'] = 'bar'
        elif 'line' in prompt_lower:
            params['chart_type'] = 'line'
        
        if 'temperature' in prompt_lower:
            params['keys'] = 'temperature'
        elif 'humidity' in prompt_lower:
            params['keys'] = 'humidity'
        elif 'battery' in prompt_lower:
            params['keys'] = 'batteryLevel'
        
        days_match = re.search(r'(\d+)\s*(day|days)', prompt_lower)
        if days_match:
            params['days_back'] = int(days_match.group(1))
        
        return params
    
    try:
        extraction_prompt = f"""
Extract parameters from this user request for a device data pipeline:

User request: "{prompt}"

Available parameters:
1. chart_type: "line" or "bar" (default: line)
2. keys: "batteryLevel", "temperature", "humidity", or combinations like "temperature,humidity" (default: batteryLevel)
3. days_back: number of days to look back (optional, if not specified fetch all data)

Respond ONLY with a JSON object containing the extracted parameters. If a parameter is not mentioned, don't include it.

Examples:
- "Get battery data" → {{"keys": "batteryLevel"}}
- "Show temperature for 7 days as bar chart" → {{"keys": "temperature", "chart_type": "bar", "days_back": 7}}
- "Create line chart of humidity" → {{"keys": "humidity", "chart_type": "line"}}
- "Fetch data for last 3 days" → {{"days_back": 3}}

JSON Response:"""

        response = model.generate_content(extraction_prompt)
        result_text = response.text.strip()
        
        # Clean up the response and extract JSON
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        try:
            params = json.loads(result_text)
            print(f"🧠 AI extracted parameters: {params}")
            return params
        except json.JSONDecodeError:
            print(f"⚠️ Could not parse AI response as JSON: {result_text}")
            return {}
            
    except Exception as e:
        print(f"❌ Error in AI parameter extraction: {e}")
        return {}

def execute_device_pipeline(params=None):
    """
    Execute the device_pipeline.py script with optional parameters
    """
    try:
        # Check if we're in a container environment
        if os.path.exists('/app/device_pipeline.py'):
            # Container environment - script is in current directory
            script_path = 'device_pipeline.py'
            cmd = ['python3', script_path]
            print(f"🐳 Using container environment")
        else:
            # Host environment - script is in AI subdirectory
            script_path = 'AI/device_pipeline.py'
            
            # Use the virtual environment python if available
            venv_python = os.path.join(os.path.dirname(__file__), '..', 'venv', 'bin', 'python3')
            if os.path.exists(venv_python):
                cmd = [venv_python, script_path]
                print(f"🐍 Using virtual environment python: {venv_python}")
            else:
                cmd = ['python3', script_path]
                print(f"🐍 Using system python3")

        # Add parameters if provided - ensure we use all parameters from smart selector
        if params:
            if 'device_id' in params:
                cmd.extend(['-d', params['device_id']])
            if 'chart_type' in params:
                cmd.extend(['-t', params['chart_type']])
            if 'keys' in params:
                cmd.extend(['-k', params['keys']])

            # Handle time range parameters
            if 'time_range' in params and params['time_range']:
                time_range = params['time_range']
                if time_range.get('hours_back'):
                    cmd.extend(['--hours', str(time_range['hours_back'])])
                elif time_range.get('days_back'):
                    cmd.extend(['-b', str(time_range['days_back'])])
                elif time_range.get('specific_day_offset') is not None:
                    # Use JSON format for complex time ranges
                    import json
                    cmd.extend(['--time-range', json.dumps(time_range)])

        print(f"🚀 Executing device pipeline with smart selector parameters:")
        print(f"   Command: {' '.join(cmd)}")
        if params:
            print(f"   � Device: {params.get('device_name', 'Unknown')} ({params.get('device_id', 'No ID')[:8]}...)")
            print(f"   🔑 Keys: {params.get('keys', 'No keys')}")
            print(f"   📊 Chart: {params.get('chart_type', 'line')}")

            # Display time range information
            if params.get('time_range'):
                time_desc = format_time_range_for_display(params['time_range'])
                print(f"   📅 Time Range: {time_desc}")

            print(f"   🎯 Confidence: {params.get('confidence', 'unknown')}")

        print(f"🔧 DEBUG: Full command being executed:")
        print(f"   {' '.join(cmd)}")

        # Determine working directory based on environment
        if os.path.exists('/app/device_pipeline.py'):
            # Container environment - work from /app
            work_dir = '/app'
        else:
            # Host environment - work from root directory (parent of AI directory)
            work_dir = os.path.dirname(os.path.dirname(__file__))
        
        print(f"🔧 DEBUG: Working directory: {work_dir}")
        print(f"🔧 DEBUG: Script path exists: {os.path.exists(os.path.join(work_dir, script_path))}")

        # Execute the pipeline
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            cwd=work_dir
        )

        print(f"🔧 DEBUG: Pipeline execution completed")
        print(f"   Return code: {result.returncode}")
        print(f"   STDOUT: {result.stdout[:500] if result.stdout else 'No stdout'}")
        print(f"   STDERR: {result.stderr[:500] if result.stderr else 'No stderr'}")

        if result.returncode == 0:
            success_message = 'Device pipeline executed successfully! 📊'
            details = 'Data fetched and charts generated. Check the plots/ folder for visualizations.'

            # Find the most recent plot file
            plot_url = None
            try:
                # Check both possible plot directories (container vs host)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                plots_dirs = [
                    os.path.join(script_dir, 'plots'),  # Container: /app/plots
                    os.path.join(script_dir, 'AI', 'plots')  # Host: /app/AI/plots  
                ]
                
                plot_files = []
                for plots_dir in plots_dirs:
                    if os.path.exists(plots_dir):
                        plot_files.extend(glob.glob(os.path.join(plots_dir, '*.png')))
                        print(f"🔍 Found {len(glob.glob(os.path.join(plots_dir, '*.png')))} plots in {plots_dir}")
                
                if plot_files:
                    # Get the most recent plot file
                    latest_plot = max(plot_files, key=os.path.getctime)
                    plot_filename = os.path.basename(latest_plot)
                    plot_url = f"http://192.168.0.1:8003/plots/{plot_filename}"
                    print(f"📊 Generated plot URL: {plot_url}")
                else:
                    print("⚠️  No plot files found in any directory")
            except Exception as e:
                print(f"⚠️  Could not determine plot URL: {e}")

            # Add detailed device info if available from smart selector
            if params:
                if 'device_name' in params:
                    details += f"\n📱 Device: {params['device_name']}"
                if 'device_id' in params:
                    details += f"\n🆔 Device ID: {params['device_id'][:8]}..."
                if 'keys' in params:
                    details += f"\n🔑 Data Keys: {params['keys']}"
                if 'chart_type' in params:
                    details += f"\n📊 Chart Type: {params['chart_type']}"
                if 'time_range' in params:
                    time_desc = format_time_range_for_display(params['time_range'])
                    details += f"\n📅 Time Range: {time_desc}"
                if 'confidence' in params:
                    details += f"\n🎯 AI Confidence: {params['confidence']}"

            response = {
                'success': True,
                'message': success_message,
                'details': details,
                'output': result.stdout.strip() if result.stdout else None,
                'params_used': params
            }

            # Add plot URL if available
            if plot_url:
                response['plot_url'] = plot_url

            return response
        else:
            return {
                'success': False,
                'message': 'Pipeline execution failed ❌',
                'error': result.stderr.strip() if result.stderr else 'Unknown error',
                'output': result.stdout.strip() if result.stdout else None,
                'params_used': params
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': 'Pipeline execution timed out ⏰',
            'error': 'The pipeline took too long to execute (>2 minutes)'
        }
    except Exception as e:
        return {
            'success': False,
            'message': 'Failed to execute pipeline ❌',
            'error': str(e)
        }

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Device Pipeline Chatbot",
        "description": "Intelligent chatbot that executes device data pipelines on demand",
        "status": "running",
        "port": 8003,
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)",
            "info": "/ (GET)"
        },
        "capabilities": {
            "smart_device_selection": "AI-powered device and parameter selection from natural language",
            "pipeline_execution": "Automatically detects and runs device_pipeline.py with optimal settings",
            "parameter_extraction": "Extracts device ID, chart type, data keys, and time range from prompts",
            "intelligent_matching": "Matches user requests to available devices and telemetry keys"
        },
        "usage": {
            "method": "POST",
            "url": "http://localhost:8003/chat",
            "body": {
                "prompt": "Your request here"
            }
        },
        "examples": [
            "Show me temperature data from the DHT11 sensor",
            "Get battery levels for the last 3 days as a bar chart",
            "Fetch humidity data and create a line chart", 
            "Display data from my battery sensor",
            "Run pipeline for device with temperature readings"
        ]
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    pipeline_script_exists = os.path.exists(os.path.join(os.path.dirname(__file__), 'device_pipeline.py'))
    api_configured = os.getenv('GOOGLE_API_KEY') is not None
    model_loaded = model is not None
    smart_selector_available = smart_device_selection is not None
    
    return jsonify({
        "status": "healthy" if pipeline_script_exists and api_configured and model_loaded else "unhealthy",
        "pipeline_script_available": pipeline_script_exists,
        "api_configured": api_configured,
        "model_loaded": model_loaded,
        "smart_device_selector": smart_selector_available,
        "service_type": "smart_ai_pipeline_chatbot",
        "timestamp": "2025-08-13"
    })

@app.route('/plots/<filename>', methods=['GET'])
def serve_plot(filename):
    """Serve generated plot images"""
    try:
        # Check both possible plot directories (container vs host)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plots_dirs = [
            os.path.join(script_dir, 'plots'),  # Container: /app/plots
            os.path.join(script_dir, 'AI', 'plots')  # Host: /app/AI/plots
        ]
        
        file_path = None
        for plots_dir in plots_dirs:
            potential_path = os.path.join(plots_dir, filename)
            if os.path.exists(potential_path):
                file_path = potential_path
                break

        # Security check - ensure file exists and is a PNG
        if not file_path or not filename.endswith('.png'):
            return jsonify({"error": "Plot not found"}), 404

        return send_file(file_path, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": f"Error serving plot: {str(e)}"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint that accepts prompts and returns AI responses or executes pipeline"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "error": "Missing 'prompt' in request body",
                "example": {
                    "prompt": "Hello, how are you?"
                }
            }), 400
        
        user_prompt = data['prompt']
        
        if not user_prompt.strip():
            return jsonify({
                "error": "Prompt cannot be empty"
            }), 400
        
        print(f"💬 Received prompt: {user_prompt[:100]}...")
        
        # Check if this is a pipeline execution request
        if is_pipeline_request(user_prompt):
            print("🔍 Detected pipeline request")

            # Extract parameters from the prompt using smart device selector
            params = extract_pipeline_params(user_prompt)
            print(f"📋 Final extracted parameters: {params}")

            # Validate that we have the minimum required parameters
            if not params or 'device_id' not in params:
                return jsonify({
                    "status": "parameter_extraction_failed",
                    "user_prompt": user_prompt,
                    "response": "❌ Could not determine which device to use for your request",
                    "details": "The smart device selector was unable to match your request to an available device. Please try being more specific about the device or data type you want.",
                    "model": "smart_device_selector"
                }), 400

            # Execute the device pipeline with smart selector parameters
            result = execute_device_pipeline(params)

            # Enhanced response with smart selector information
            response_data = {
                "status": "pipeline_executed" if result['success'] else "pipeline_failed",
                "user_prompt": user_prompt,
                "response": result['message'],
                "details": result.get('details', ''),
                "pipeline_result": result,
                "model": "smart_device_selector + device_pipeline_executor",
                # Flatten the important fields for frontend compatibility
                "success": result['success'],
                "message": result['message']
            }

            # Add plot_url if available
            if 'plot_url' in result:
                response_data['plot_url'] = result['plot_url']

            # Add smart selector metadata to response
            if params:
                response_data["smart_selector_info"] = {
                    "device_selected": params.get('device_name', 'Unknown'),
                    "confidence": params.get('confidence', 'unknown'),
                    "parameters_extracted": {
                        "device_id": params.get('device_id', 'None')[:8] + "..." if params.get('device_id') else 'None',
                        "keys": params.get('keys', 'None'),
                        "chart_type": params.get('chart_type', 'None'),
                        "time_range": format_time_range_for_display(params.get('time_range', {})) if params.get('time_range') else 'None'
                    }
                }

            return jsonify(response_data)
        
        else:
            # Not a pipeline request - return standard response
            return jsonify({
                "status": "standard_response",
                "user_prompt": user_prompt,
                "response": "I'm a specialized device data pipeline bot. I can help you fetch and visualize device data by running pipelines. Try asking me to 'run the device pipeline' or 'fetch battery data' to get started!",
                "model": "pipeline_bot"
            })
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to quickly check if the chatbot is working"""
    test_prompt = "Hello! Can you tell me what you are?"
    
    if not model:
        return jsonify({
            "error": "AI model not available",
            "test_prompt": test_prompt,
            "response": "Model not configured"
        })
    
    try:
        response = model.generate_content(test_prompt)
        return jsonify({
            "status": "test_successful",
            "test_prompt": test_prompt,
            "response": response.text,
            "model": "models/gemini-1.5-flash"
        })
    except Exception as e:
        return jsonify({
            "error": f"Test failed: {str(e)}",
            "test_prompt": test_prompt
        })

def main():
    """Main function to start the device pipeline chatbot server"""
    print("🤖 Starting AI-Powered Device Pipeline Chatbot")
    print("=" * 50)
    print("📡 Server will run on: http://192.168.0.1:8003")
    print("💬 Chat endpoint: http://192.168.0.1:8003/chat")
    print("🔍 Health check: http://192.168.0.1:8003/health")
    print()
    print("🎯 This chatbot can:")
    print("  • Use AI to intelligently detect pipeline requests")
    print("  • Extract parameters using natural language understanding")
    print("  • Run device_pipeline.py automatically")
    print("  • Generate data visualizations")
    print()
    print("📝 Example prompts:")
    print("  • 'Run the device pipeline'")
    print("  • 'Fetch battery data and create a chart'")
    print("  • 'Get temperature data for the last 7 days'")
    print("  • 'Execute pipeline with bar chart'")
    print()
    
    # Check API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  WARNING: GOOGLE_API_KEY not set!")
        print("   Set it with: export GOOGLE_API_KEY='your_api_key_here'")
        print("   The AI decision-making will use fallback keyword detection.")
    else:
        print("✅ Google AI API configured")
    
    # Check if pipeline script exists
    pipeline_script = os.path.join(os.path.dirname(__file__), 'device_pipeline.py')
    if not os.path.exists(pipeline_script):
        print("⚠️  WARNING: device_pipeline.py not found!")
        print(f"   Expected at: {pipeline_script}")
        print("   The chatbot will not be able to execute pipelines.")
    else:
        print("✅ device_pipeline.py found and ready")
    
    # Check model status
    if model:
        print("✅ Gemini AI model loaded successfully")
    else:
        print("⚠️  AI model not loaded - using fallback detection")
    
    print("🚀 Starting server...")
    
    try:
        app.run(host='0.0.0.0', port=8003, debug=False)
    except KeyboardInterrupt:
        print("\n👋 AI-Powered Pipeline Chatbot stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
