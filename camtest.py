import paramiko
import urllib.request
import cv2
import numpy as np
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk

class MJPEGStreamer:
    def __init__(self, root, stream_url):
        self.root = root
        self.stream_url = stream_url
        self.video_label = Label(root)
        self.video_label.pack()
        self.update_frame()

    def update_frame(self):
        try:
            with urllib.request.urlopen(self.stream_url) as stream:
                byte_arr = bytearray()
                while True:
                    byte_arr.extend(stream.read(1024))
                    start_idx = byte_arr.find(b'\xff\xd8')  # JPEG start
                    end_idx = byte_arr.find(b'\xff\xd9')  # JPEG end
                    if start_idx != -1 and end_idx != -1:
                        jpg = byte_arr[start_idx:end_idx+2]
                        byte_arr = byte_arr[end_idx+2:]
                        image = np.asarray(bytearray(jpg), dtype="uint8")
                        frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame)
                        imgtk = ImageTk.PhotoImage(image=img)
                        self.video_label.imgtk = imgtk
                        self.video_label.configure(image=imgtk)
                        break
            self.root.after(10, self.update_frame)
        except Exception as e:
            print(f"Failed to update frame: {e}")
            self.root.after(1000, self.update_frame)

class RaspberryPiController:
    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect()

    def connect(self):
        try:
            self.ssh_client.connect(self.ip, username=self.user, password=self.password)
            print("Connected to Raspberry Pi")
        except Exception as e:
            print(f"Failed to connect to Raspberry Pi: {e}")

    def install_mjpeg_streamer(self):
        try:
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y cmake libjpeg8-dev",
                "git clone https://github.com/jacksonliam/mjpg-streamer.git",
                "cd mjpg-streamer/mjpg-streamer-experimental && make",
                "sudo make install"
            ]
            for command in commands:
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                for line in stdout:
                    print(f"STDOUT: {line.strip()}")
                for line in stderr:
                    print(f"STDERR: {line.strip()}")
            print("Installed mjpeg-streamer on Raspberry Pi")
        except Exception as e:
            print(f"Failed to install mjpeg-streamer: {e}")

    def start_mjpeg_streamer(self):
        try:
            command = "cd mjpg-streamer/mjpg-streamer-experimental && ./mjpg_streamer -i \"./input_raspicam.so\" -o \"./output_http.so -w ./www -p 8080\""
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            for line in stdout:
                print(f"STDOUT: {line.strip()}")
            for line in stderr:
                print(f"STDERR: {line.strip()}")
            print("Started mjpeg-streamer on Raspberry Pi")
        except Exception as e:
            print(f"Failed to start mjpeg-streamer: {e}")

    def close(self):
        if self.ssh_client:
            self.ssh_client.close()
            print("SSH session closed")

if __name__ == "__main__":
    pi_ip = "200.10.10.2"  # Replace with your Raspberry Pi IP address
    pi_user = "pi"  # Replace with your Raspberry Pi username
    pi_password = "nanotube"  # Replace with your Raspberry Pi password
    stream_url = f"http://{pi_ip}:8080/?action=stream"

    root = tk.Tk()
    app = MJPEGStreamer(root, stream_url)

    pi_controller = RaspberryPiController(pi_ip, pi_user, pi_password)
    pi_controller.install_mjpeg_streamer()
    pi_controller.start_mjpeg_streamer()

    root.mainloop()
    pi_controller.close()
