import webview
import sys
import threading
from app import app
import time

def start_server():
    """Start Flask server without reloader (required for PyInstaller)"""
    app.run(port=5000, debug=False, use_reloader=False, threaded=True)

if __name__ == '__main__':
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Give server more time to start
    time.sleep(2)

    # Create a native window pointing to the Flask app
    webview.create_window(
        'E-Kejaksaan Tracking System', 
        'http://127.0.0.1:5000',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False
    )
    
    # Start the GUI loop
    webview.start()
    sys.exit()
