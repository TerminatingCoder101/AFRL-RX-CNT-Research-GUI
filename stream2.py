from picamera2 import Picamera2
import socket
import time
import io

def start_stream():
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (400, 400)})
    picam2.configure(config)
    picam2.start()

    # Set up UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(2)  # Camera warm-up time

    print("Starting camera stream...")
    while True:
        buffer = io.BytesIO()
        picam2.capture_file(buffer, format='jpeg')
        buffer.seek(0)
        client_socket.sendto(buffer.read(), ('<LOCAL_COMPUTER_IP>', 8000))
        print("Frame sent")
        time.sleep(0.1)  # Adjust this as needed to control frame rate

if __name__ == '__main__':
    print("Script started")
    start_stream()
