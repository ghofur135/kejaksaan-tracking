import webview
import sys
import threading
from app import app
import time

def start_server():
    app.run(port=5000, debug=False)

if __name__ == '__main__':
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Give server a second to start
    time.sleep(1)

    # Create a native window pointing to the Flask app
    webview.create_window(
        'E-Kejaksaan Tracking System', 
        'http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True
    )
    
    # Start the GUI loop
    webview.start()
    sys.exit()
