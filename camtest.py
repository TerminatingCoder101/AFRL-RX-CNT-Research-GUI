import paramiko
from threading import Thread
import socket
import cv2
from tkinter import *
from PIL import Image, ImageTk
import numpy as np

class RPiCameraStream:
    def __init__(self, master):
        self.master = master
        self.video_label = Label(master)
        self.video_label.pack()
        self.running = False
        self.ssh_client = None
        self.ip_entry = Entry(master)
        self.user_entry = Entry(master)
        self.pass_entry = Entry(master)

        self.shutter_speed = 0  # Set default shutter speed
        self.iso = 0  # Set default ISO

    def connect_to_raspberry_pi(self):
        global shutter_speed
        global iso
        local_ip = socket.gethostname()
        ip = self.ip_entry.get()  # e.g., 200.10.10.2
        user = self.user_entry.get()  # e.g., pi
        password = self.pass_entry.get()  # e.g., nanotube
        print("Connecting to Raspberry Pi")
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(ip, username=user, password=password)
            print("Connected to Raspberry Pi")
            self.start_raspberry_pi_camera_stream(ip, local_ip, user, password)
        except Exception as e:
            print(f"Failed to connect to Raspberry Pi: {e}")

    def start_raspberry_pi_camera_stream(self, ip, local_ip, user, password):
        self.running = True
        self.video_label.configure(width=400, height=400)
        Thread(target=self.update_raspberry_pi_frame).start()

        # Start the streaming script on the Raspberry Pi
        try:
            ssh_command = f"python3 /home/pi/stream.py --ipaddr {local_ip}"
            self.ssh_client.exec_command(ssh_command)
        except Exception as e:
            print(f"Failed to start streaming script on Raspberry Pi: {e}")

    def update_raspberry_pi_frame(self):
        # Set up UDP socket to receive the stream
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('', 2222))

        while self.running:
            try:
                # Receive data from the socket
                data, _ = udp_socket.recvfrom(65536)
                # Convert the data to a numpy array
                np_data = np.frombuffer(data, dtype=np.uint8)
                # Decode the image
                frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

                if frame is not None:
                    # Convert the frame to ImageTk format
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    imgtk = ImageTk.PhotoImage(image=image)
                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)

            except Exception as e:
                print(f"Failed to update frame from Raspberry Pi Camera: {e}")
                break

if __name__ == "__main__":
    root = Tk()
    app = RPiCameraStream(root)
    root.mainloop()
