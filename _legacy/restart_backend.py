#!/usr/bin/env python3
"""
Script to restart the FastAPI backend server
Run this to restart the server with the latest code changes
"""

import subprocess
import sys
import time
import requests

def check_if_server_running():
    """Check if the backend server is currently running"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        return True
    except:
        return False

def kill_server_process():
    """Kill any running backend server processes"""
    try:
        # Try to kill uvicorn processes
        subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
        subprocess.run(['pkill', '-f', 'main.py'], capture_output=True)
        print("Killed existing server processes")
        time.sleep(2)  # Wait for processes to terminate
    except Exception as e:
        print(f"Note: Could not kill existing processes: {e}")

def start_server():
    """Start the FastAPI backend server"""
    print("Starting FastAPI backend server...")
    try:
        # Start the server in the background
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"Server process started with PID: {process.pid}")
        print("Server should be available at: http://127.0.0.1:8000")
        print("Health check endpoint: http://127.0.0.1:8000/health")

        # Wait a bit and check if server started successfully
        time.sleep(3)
        if check_if_server_running():
            print("Server started successfully!")
            print("You can now test the chat endpoint with: http://127.0.0.1:8000/chat")
        else:
            print("Server failed to start. Check the logs above.")

        return process

    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def main():
    """Main function to restart the backend server"""
    print("Restarting FastAPI Backend Server")
    print("=" * 50)

    # Check if server is currently running
    if check_if_server_running():
        print("Backend server is currently running")
        print("Stopping existing server...")

        # Kill existing processes
        kill_server_process()

        # Verify it's stopped
        if check_if_server_running():
            print("Failed to stop existing server")
            return
        else:
            print("Existing server stopped")

    # Start new server
    print("\nStarting new server...")
    process = start_server()

    if process:
        print("\n" + "=" * 50)
        print("Backend server restarted successfully!")
        print("\nNext steps:")
        print("1. Start your frontend: cd frontend && npm start")
        print("2. Test the backend: python test_backend.py")
        print("3. Open http://localhost:3000 to use the chat interface")

        # Keep the script running so the server stays alive
        try:
            print("\nServer is running. Press Ctrl+C to stop...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping server...")
            process.terminate()
            print("Server stopped")

if __name__ == "__main__":
    main()