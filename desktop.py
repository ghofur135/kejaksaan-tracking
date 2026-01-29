import webview
import sys
import threading
from app import app
import time
import socket

def find_free_port():
    """Find a free port to use"""
    ports_to_try = [5000, 5001, 5002, 5003, 8000, 8080, 8888]
    
    for port in ports_to_try:
        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    
    # If all ports are taken, use a random free port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def start_server(port):
    """Start Flask server without reloader (required for PyInstaller)"""
    try:
        print(f"Starting Flask server on port {port}...")
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Find a free port
    port = find_free_port()
    print(f"Using port: {port}")
    
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server, args=(port,))
    t.daemon = True
    t.start()
    
    # Give server more time to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Test if server is running
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result != 0:
            print(f"ERROR: Server failed to start on port {port}")
            print("Please check:")
            print("1. Firewall/Antivirus settings")
            print("2. Port is not blocked")
            print("3. Database connection is working")
            input("Press Enter to exit...")
            sys.exit(1)
        else:
            print(f"Server is running on http://127.0.0.1:{port}")
    except Exception as e:
        print(f"Error checking server: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Create a native window pointing to the Flask app
    try:
        webview.create_window(
            'E-Kejaksaan Tracking System', 
            f'http://127.0.0.1:{port}',
            width=1400,
            height=900,
            resizable=True,
            fullscreen=False
        )
        
        # Start the GUI loop
        webview.start()
    except Exception as e:
        print(f"Error creating window: {e}")
        input("Press Enter to exit...")
    
    sys.exit()
