
import socket
import cv2

def start_stream(ip, port):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print('Failed to open camera')
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))

    while True:
        ret, frame = cap.read()
        if not ret:
            print('Failed to grab frame')
            break

        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()
        size = len(data)

        client_socket.sendall(size.to_bytes(4, byteorder='big'))
        client_socket.sendall(data)

    cap.release()
    client_socket.close()

start_stream('{self.local_ip}', {self.local_port})
