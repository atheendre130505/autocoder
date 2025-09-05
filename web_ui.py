#!/usr/bin/env python3
"""
Web UI for Autonomous Autocoder
Flask-based web interface for real-time project creation and monitoring.
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_mode import AutonomousAutocoder
from core import config, logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'autocoder_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global autocoder instance
autocoder = None
current_projects = []

def init_autocoder():
    """Initialize the autonomous autocoder."""
    global autocoder
    autocoder = AutonomousAutocoder()
    logger.info("Web UI initialized with autonomous autocoder")

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Get current status."""
    if autocoder:
        status = autocoder.get_status()
        return jsonify({
            "success": True,
            "status": status,
            "config": {
                "autonomous_mode": config.AUTONOMOUS_MODE,
                "auto_install_deps": config.AUTO_INSTALL_DEPS,
                "auto_execute_projects": config.AUTO_EXECUTE_PROJECTS
            }
        })
    return jsonify({"success": False, "error": "Autocoder not initialized"})

@app.route('/api/projects')
def api_projects():
    """Get list of created projects."""
    if autocoder:
        status = autocoder.get_status()
        return jsonify({
            "success": True,
            "projects": status.get('projects', [])
        })
    return jsonify({"success": False, "error": "Autocoder not initialized"})

@app.route('/api/project/<project_name>')
def api_project_details(project_name):
    """Get details of a specific project."""
    if autocoder:
        status = autocoder.get_status()
        projects = status.get('projects', [])
        
        for project in projects:
            if project['name'] == project_name:
                # Get project files
                project_path = project['path']
                files = []
                
                if os.path.exists(project_path):
                    for root, dirs, filenames in os.walk(project_path):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            rel_path = os.path.relpath(file_path, project_path)
                            
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                files.append({
                                    "name": filename,
                                    "path": rel_path,
                                    "content": content,
                                    "size": len(content)
                                })
                            except Exception as e:
                                files.append({
                                    "name": filename,
                                    "path": rel_path,
                                    "content": f"Error reading file: {e}",
                                    "size": 0
                                })
                
                return jsonify({
                    "success": True,
                    "project": project,
                    "files": files
                })
        
        return jsonify({"success": False, "error": "Project not found"})
    
    return jsonify({"success": False, "error": "Autocoder not initialized"})

@app.route('/api/create', methods=['POST'])
def api_create_project():
    """Create a new project."""
    data = request.get_json()
    request_text = data.get('request', '')
    
    if not request_text:
        return jsonify({"success": False, "error": "No request provided"})
    
    if not autocoder:
        return jsonify({"success": False, "error": "Autocoder not initialized"})
    
    # Emit start event
    socketio.emit('project_start', {
        'request': request_text,
        'timestamp': datetime.now().isoformat()
    })
    
    # Process in background thread
    def process_project():
        try:
            result = autocoder.process_request(request_text)
            
            if result['success']:
                # Emit success event
                socketio.emit('project_success', {
                    'project_name': result['project_name'],
                    'project_path': result['project_path'],
                    'files_created': len(result['created_files']),
                    'execution_info': result.get('execution_info', {}),
                    'timestamp': datetime.now().isoformat()
                })
            else:
                # Emit error event
                socketio.emit('project_error', {
                    'error': result.get('error', 'Unknown error'),
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            socketio.emit('project_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    # Start background thread
    thread = threading.Thread(target=process_project)
    thread.daemon = True
    thread.start()
    
    return jsonify({"success": True, "message": "Project creation started"})

@app.route('/api/execute/<project_name>')
def api_execute_project(project_name):
    """Execute a specific project."""
    if not autocoder:
        return jsonify({"success": False, "error": "Autocoder not initialized"})
    
    status = autocoder.get_status()
    projects = status.get('projects', [])
    
    for project in projects:
        if project['name'] == project_name:
            project_path = project['path']
            project_type = project['type']
            
            # Execute the project
            try:
                exec_result = autocoder.qwen._execute_project(project_path, project_type)
                
                return jsonify({
                    "success": True,
                    "execution": exec_result
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                })
    
    return jsonify({"success": False, "error": "Project not found"})

@app.route('/api/save/<project_name>', methods=['POST'])
def api_save_file(project_name):
    """Save a file in a project."""
    if not autocoder:
        return jsonify({"success": False, "error": "Autocoder not initialized"})
    
    data = request.get_json()
    file_path = data.get('filePath', '')
    content = data.get('content', '')
    
    if not file_path or content is None:
        return jsonify({"success": False, "error": "Missing filePath or content"})
    
    status = autocoder.get_status()
    projects = status.get('projects', [])
    
    for project in projects:
        if project['name'] == project_name:
            project_path = project['path']
            full_file_path = os.path.join(project_path, file_path)
            
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                
                # Write file
                with open(full_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"File saved: {full_file_path}")
                return jsonify({"success": True, "message": "File saved successfully"})
                
            except Exception as e:
                logger.error(f"Error saving file {full_file_path}: {e}")
                return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"success": False, "error": "Project not found"})

@app.route('/api/download/<project_name>')
def api_download_project(project_name):
    """Download project as zip file."""
    if not autocoder:
        return jsonify({"success": False, "error": "Autocoder not initialized"})
    
    status = autocoder.get_status()
    projects = status.get('projects', [])
    
    for project in projects:
        if project['name'] == project_name:
            project_path = project['path']
            
            # Create zip file
            import zipfile
            import tempfile
            
            zip_path = os.path.join(tempfile.gettempdir(), f"{project_name}.zip")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_path)
                        zipf.write(file_path, arcname)
            
            return send_from_directory(
                os.path.dirname(zip_path),
                os.path.basename(zip_path),
                as_attachment=True,
                download_name=f"{project_name}.zip"
            )
    
    return jsonify({"success": False, "error": "Project not found"})

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to Autocoder Web UI'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    pass

if __name__ == '__main__':
    # Initialize autocoder
    init_autocoder()
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting Autocoder Web UI...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🤖 Autonomous mode enabled!")
    
    # Run the app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
