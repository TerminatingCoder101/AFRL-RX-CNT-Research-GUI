import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import paramiko
import threading
from threading import Thread
from datetime import date
import os
import getpass
import platform
import numpy as np
import time
import subprocess
import socket

counter = 1
file_name = ""
shutter_speed = 0
iso = 0
experiment_name = "Hi"
folder_path = "Downloads/AFRL_RX_GUI"

class GUI:

    def __init__(self, root):
        counter = 1
        user1 = getpass.getuser()
        system1 = platform.system()
        self.root = root
        self.root.configure(background='light blue')
        self.root.resizable(height=True, width=True)
        self.root.title("RX GUI Control")

        # ROOT
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
       # self.root.grid_columnconfigure(2, weight=2)

        # VIDEO FRAME
        self.video_frame = ttk.LabelFrame(root, text="Video Stream")
        self.video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_label = tk.Label(self.video_frame, bg="black", fg="white")
        self.video_label.grid(row=0, column=0, sticky="nsew")
        self.video_thread = None

        # FILE AND INFO
        # self.label_frame = ttk.LabelFrame(root, text="Info")
        # self.label_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        # self.label_frame.grid_rowconfigure(4, weight=1)
        # self.label_frame.grid_columnconfigure(0, weight=1)
        # self.label_user = tk.Label(self.label_frame, text=f"User: {user1}")
        # self.label_user.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        # self.label_system = tk.Label(self.label_frame, text=f"System: {system1}")
        # self.label_system.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
        # self.label_text = tk.Label(self.label_frame, text="Label of File")
        # self.label_text.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
        # self.label_name = tk.Label(self.label_frame, text="")
        # self.label_name.grid(row=3, column=0, pady=10, padx=10, sticky="nsew")

        self.label_frame = ttk.LabelFrame(root, text="Info")
        self.label_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.label_frame.grid_rowconfigure(5, weight=1)
        self.label_frame.grid_columnconfigure(0, weight=1)
        self.label_user = tk.Label(self.label_frame, text=f"User: {user1}")
        self.label_user.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        self.label_system = tk.Label(self.label_frame, text=f"System: {system1}")
        self.label_system.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
        self.label_name = tk.Label(self.label_frame, text="")
        self.label_name.grid(row=3, column=0, pady=10, padx=10, sticky="nsew")
        self.file_name_entry = tk.Entry(self.label_frame)
        self.file_name_entry.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
        self.save_button2 = tk.Button(self.label_frame, text="Save", command=self.save_image)
        self.save_button2.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

        # IMAGE CONTROL

        # IMAGE CONTROL
        self.control_frame = ttk.LabelFrame(root, text="Image Control")
        self.control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid_rowconfigure(3, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)
        self.preview_button = tk.Button(self.control_frame, text="Preview", command=self.start_preview)
        self.preview_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.capture_button = tk.Button(self.control_frame, text="Capture", command=self.capture_image)
        self.capture_button.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.iso_label = tk.Label(self.control_frame, text="IS0:")
        self.iso_label.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.iso_entry = tk.Entry(self.control_frame)
        self.iso_entry.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.ss_label = tk.Label(self.control_frame, text="SS:")
        self.ss_label.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.ss_entry = tk.Entry(self.control_frame)
        self.ss_entry.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.save_button1 = tk.Button(self.control_frame, text="Save", command=self.save_iso_ss)
        self.save_button1.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        # RPi INTERFACE
        self.connection_frame = ttk.LabelFrame(root, text="Connection to RPi")
        self.connection_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.connection_frame.grid_rowconfigure(3, weight=1)
        self.connection_frame.grid_columnconfigure(1, weight=1)
        self.ip_label = tk.Label(self.connection_frame, text="IP:")
        self.ip_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.ip_entry = tk.Entry(self.connection_frame)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.user_label = tk.Label(self.connection_frame, text="User:")
        self.user_label.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.user_entry = tk.Entry(self.connection_frame)
        self.user_entry.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.pass_label = tk.Label(self.connection_frame, text="Pass:")
        self.pass_label.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.pass_entry = tk.Entry(self.connection_frame, show="*")
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.connect_button = tk.Button(self.connection_frame, text='Connect', command=self.connect_to_raspberry_pi)
        self.connect_button.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        # CAPTURE PIC
        self.video_capt = ttk.LabelFrame(root, text="Captured Image")
        self.video_capt.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.video_capt.grid_rowconfigure(0, weight=1)
        self.video_capt.grid_columnconfigure(2, weight=1)
        self.video_capt_label = tk.Label(self.video_capt, bg="black", fg="white")
        self.video_capt_label.grid(row=0, column=2, sticky="nsew")
        self.video_capt_label.configure(width=30)

        # FFT CONTROL
        self.fft_frame = ttk.LabelFrame(root, text="FFT Control")
        self.fft_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.fft_frame.grid_rowconfigure(0, weight=1)
        self.fft_frame.grid_columnconfigure(0, weight=1)
        self.fft_label = tk.Label(self.fft_frame, bg="black", fg="white")
        self.fft_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # RUN
        self.cap = None
        self.ssh_client = None
        self.running = False
        self.captured_frame = None

    ################################### MANUAL CAMERA ##################################

    def start_preview(self):  # For manual use only
        self.running = True
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera")
            return
        self.video_label.configure(width=400, height=400)
        
       # self.fft_app = FFTApp(self.cap, self.fft_label)
        
        self.video_thread = Thread(target=self.update_frame)
        #self.fft_thread = Thread(target=self.fft_app.start)
        
        self.video_thread.start()
        #self.fft_thread.start()

    def update_frame(self):  # For manual use only
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            else:
                print("Failed to read frame")
            self.root.after(10, self.update_frame)

    def capture_image(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.captured_frame = frame
                self.populate_file_name_entry()
                self.video_capt_label.configure(width=400, height=400)
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_capt_label.imgtk = imgtk
                self.video_capt_label.configure(image=imgtk)

    def populate_file_name_entry(self):
        global experiment_name
        global counter
        today = date.today()
        curr_date = today.strftime("%y%m%d")
        if not self.file_name_entry.get():
            print("Inside if not")
            default_file_name = f"{curr_date}_{counter}_{experiment_name}.png"
            self.file_name_entry.insert(0, default_file_name)  # Insert default file name
            counter+=1
        else:
            default_file_name = f"{curr_date}_{counter}_{experiment_name}.png"
            self.file_name_entry.delete(0, tk.END)  # Clear existing content
            self.file_name_entry.insert(0, default_file_name)  # Insert default file name
            counter+=1

    def save_image(self):
        ret = False
        if self.captured_frame is not None:
            frame = self.captured_frame
            ret = True
        global experiment_name
        global counter
        today = date.today()
        curr_date = today.strftime("%y%m%d")
        if ret:        
            global file_name
            user = getpass.getuser()
            if platform.system() == "Windows":
                filePath = f"C:/{user}/{folder_path}"
            elif platform.system() == "Darwin":
                filePath = f"/Users/{user}/{folder_path}"

            if not self.file_name_entry.get():
                default_file_name = f"{curr_date}_{counter}_{experiment_name}.png"
                self.file_name_entry.insert(0, default_file_name)
            file_name = self.file_name_entry.get()
            cv2.imwrite(os.path.join(filePath, file_name), frame)
            print(f"Captured image saved as {file_name} at {filePath}")
            self.label_name.configure(text=f"{file_name} at {filePath}")

    def save_iso_ss(self):
        global shutter_speed
        global iso
        shutter_speed = self.ss_entry.get()
        iso = self.iso_entry.get()
        print(f"Shutter Speed saved: {shutter_speed}")
        print(f"ISO saved: {iso}")

    ################################### RPi CAMERA ##################################        

    # def connect_to_raspberry_pi(self):
    #     global shutter_speed
    #     global iso
    #     ip = self.ip_entry.get() #200.10.10.2
    #     user = self.user_entry.get() #pi
    #     password = self.pass_entry.get() #nanotube
    #     print("Connecting to Raspberry Pi")
    #     try:
    #         self.ssh_client = paramiko.SSHClient()
    #         self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #         self.ssh_client.connect(ip, username=user, password=password)
    #         print("Connected to Raspberry Pi")
    #         self.start_raspberry_pi_camera_stream(ip, user, password, shutter_speed, iso)
    #     except Exception as e:
    #         print(f"Failed to connect to Raspberry Pi: {e}")

    # def start_raspberry_pi_camera_stream(self, ip, user, password, shutter_speed, iso):
    #     self.running = True
    #     self.video_label.configure(width=400, height=400)
    #     threading.Thread(target=self.update_raspberry_pi_frame, args=(ip, user, password, shutter_speed, iso)).start()

    # def update_raspberry_pi_frame(self, ip, user, password, shutter_speed, iso):
    #     while self.running:
    #         try:
    #             ssh_command = f"raspivid -t 0 -o - -ss {shutter_speed} -ISO {iso} | nc -l -p 2222 2>/dev/null"
    #             #ssh_command = f"raspivid -t 0 -o - -ss {shutter_speed} -ISO {iso} -w 640 -h 480 -fps 30 -b 1000000 | nc -l -u -p 2222 2>/dev/null"

    #             self.ssh_client.exec_command(ssh_command)
    #             time.sleep(2)
    #             self.cap = cv2.VideoCapture(f"tcp://{ip}:22")
    #             #self.cap = cv2.VideoCapture(f"udp://{ip}:22")

    #             print("Connected to RPi Camera")
    #             while self.cap.isOpened() and self.running:
    #                 ret, frame = self.cap.read()
    #                 if ret:
    #                     # cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #                     # img = Image.fromarray(cv2image)
    #                     # imgtk = ImageTk.PhotoImage(image=img)
    #                     # self.video_label.imgtk = imgtk
    #                     # self.video_label.configure(image=imgtk)
    #                     self.video_label.imgtk = frame
    #                     self.video_label.configure(image=self.video_label.imgtk)
    #                     #fft_app = FFTApp(frame, self.fft_label)
    #                     #fft_app.start()
    #                 else:
    #                     break
    #         except Exception as e:
    #             print(f"Failed to update frame from Raspberry Pi Camera: {e}")
    #             break

###################################################################################################


    # def connect_to_raspberry_pi(self):
    #     global shutter_speed
    #     global iso
    #     ip = self.ip_entry.get()  # 200.10.10.2
    #     user = self.user_entry.get()  # pi
    #     password = self.pass_entry.get()  # nanotube
    #     print("Connecting to Raspberry Pi")
    #     try:
    #         self.ssh_client = paramiko.SSHClient()
    #         self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #         self.ssh_client.connect(ip, username=user, password=password)
    #         print("Connected to Raspberry Pi")
    #         self.start_raspberry_pi_camera_stream(ip, user, password, shutter_speed, iso)
    #     except Exception as e:
    #         print(f"Failed to connect to Raspberry Pi: {e}")

    # def start_raspberry_pi_camera_stream(self, ip, user, password, shutter_speed, iso):
    #     self.running = True
    #     self.video_label.configure(width=400, height=400)
    #     Thread(target=self.update_raspberry_pi_frame, args=(ip, user, password, shutter_speed, iso)).start()

    # def update_raspberry_pi_frame(self, ip, user, password, shutter_speed, iso):
    #         while self.running:
    #             try:
    #                 ssh_command = f"raspivid -t 0 -o - -ss {shutter_speed} -ISO {iso} | nc -l -p 2222 2>/dev/null"
    #                 #ssh_command = f"raspivid -t 0 -o - -ss {shutter_speed} -ISO {iso} -w 640 -h 480 -fps 30 -b 1000000 | nc -l -u -p 2222 2>/dev/null"

    #                 self.ssh_client.exec_command(ssh_command)
    #                 time.sleep(2)
    #                 self.cap = cv2.VideoCapture(f"tcp://{ip}:22")
    #                 #self.cap = cv2.VideoCapture(f"udp://{ip}:22")

    #                 if self.cap:
    #                     print("Connected to RPi Camera")
    #                 else:
    #                     print("Not connected to RPi Camera")
    #                 while self.cap.isOpened() and self.running:
    #                     ret, frame = self.cap.read()
    #                     if ret:
    #                         self.video_label.imgtk = frame
    #                         self.video_label.configure(image=self.video_label.imgtk)
    #                     else:
    #                         break
    #             except Exception as e:
    #                 print(f"Failed to update frame from Raspberry Pi Camera: {e}")
    #                 break
    
		###############################################################################################
    def connect_to_raspberry_pi(self):
        global shutter_speed
        global iso
        ip = self.ip_entry.get()  # 200.10.10.2
        user = self.user_entry.get()  # pi
        password = self.pass_entry.get()  # nanotube
        print("Connecting to Raspberry Pi")
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(ip, username=user, password=password)
            print("Connected to Raspberry Pi")
            self.start_raspberry_pi_camera_stream(ip, user, password, shutter_speed, iso)
        except Exception as e:
            print(f"Failed to connect to Raspberry Pi: {e}")

    def start_raspberry_pi_camera_stream(self, ip, user, password, shutter_speed, iso):
        self.running = True
        self.video_label.configure(width=400, height=400)
        threading.Thread(target=self.update_raspberry_pi_frame, args=(ip, user, password, shutter_speed, iso)).start()

    def update_raspberry_pi_frame(self, ip, user, password, shutter_speed, iso):
        try:
            local_ip = '0.0.0.0'
            local_port = 2222
            ssh_command = f"raspivid -t 0 -o - -ss {shutter_speed} -ISO {iso} | nc {local_ip} {local_port}"
            
            stdin, stdout, stderr = self.ssh_client.exec_command(ssh_command)
            time.sleep(2)
            
            # Ensure the server is running on the specified port
            self.cap = cv2.VideoCapture(f"tcp://{ip}:{local_port}")
            if not self.cap.isOpened():
                print("Failed to open capture device")
                return
            
            print("Connected to RPi Camera")
            while self.cap.isOpened() and self.running:
                ret, frame = self.cap.read()
                if ret:
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    img = Image.fromarray(cv2image)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)
                else:
                    break

        except Exception as e:
            print(f"Failed to update frame from Raspberry Pi Camera: {e}")

        finally:
            if self.cap:
                self.cap.release()
            if self.ssh_client:
                self.ssh_client.close()
            print("SSH session closed")


    def close(self):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.ssh_client:
            self.ssh_client.close()
        if self.video_thread:
            self.video_thread.join()
       # if self.fft_thread:
       #     self.fft_thread.join()    
       # if self.fft_app:
        #   self.fft_app.stop()
        self.root.destroy()        


class FFTApp:

    def __init__(self, cap, fft_label):
        self.cap = cap
        self.fft_label = fft_label
        self.running = False

    def start(self):  # This should run in a separate thread
        self.running = True
        while self.running:
            self.apply_fft()

    def stop(self):
        self.running = False

    def apply_fft(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture image")
                self.stop()
                return

            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dft = cv2.dft(np.float32(gray_image), flags=cv2.DFT_COMPLEX_OUTPUT)
            dft_shift = np.fft.fftshift(dft)
            magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))

            cv2.normalize(magnitude_spectrum, magnitude_spectrum, 0, 255, cv2.NORM_MINMAX)
            magnitude_spectrum = np.uint8(magnitude_spectrum)
            img = Image.fromarray(magnitude_spectrum)
            imgtk = ImageTk.PhotoImage(image=img)
            self.fft_label.configure(width=400, height=400)
            self.fft_label.imgtk = imgtk
            self.fft_label.configure(image=imgtk)
        else:
            print("No image captured to apply FFT.")
        self.fft_label.after(10, self.apply_fft())


class RaspberryPiCameraStreamer:
    def __init__(self, pi_ip, pi_user, pi_password, local_ip, shutter_speed, iso):
        self.pi_ip = pi_ip
        self.pi_user = pi_user
        self.pi_password = pi_password
        self.local_ip = local_ip
        self.shutter_speed = shutter_speed
        self.iso = iso
        self.ssh_client = None
        self.cap = None
        self.running = True

    def start_ssh_session(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.pi_ip, username=self.pi_user, password=self.pi_password)
        print("SSH session started")

    def start_streaming(self):
        ssh_command = (
            f"libcamera-vid -t 0 --inline --width 400 --height 400 --framerate 30 "
            f"--shutter {self.shutter_speed} --gain {self.iso} -o - | "
            f"gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! "
            f"udpsink host={self.local_ip} port=5000"
        )
        self.ssh_client.exec_command(ssh_command)
        time.sleep(2)  # Give some time for the stream to start


    def receive_stream(self):
        print("recieving started")
        self.cap = cv2.VideoCapture(f"udp://{self.local_ip}:5000")
        if self.cap.isOpened():
            self.video_label.configure(width=400, height=400)
            print("Connected to Raspberry Pi Camera")
        else:
            print("Failed to connect to Raspberry Pi Camera")
            return

        while self.cap.isOpened() and self.running:
            ret, frame = self.cap.read()
            if ret:
                cv2.imshow(frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
            else:
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def stop_ssh_session(self):
        if self.ssh_client:
            self.ssh_client.close()
            print("SSH session closed")

    def start(self):
        self.start_ssh_session()

        # Start the streaming thread
        streaming_thread = threading.Thread(target=self.start_streaming)
        streaming_thread.start()

        # Start the receiving thread
        receiving_thread = threading.Thread(target=self.receive_stream)
        receiving_thread.start()

        # Wait for both threads to finish
        try:
            while receiving_thread.is_alive():
                receiving_thread.join(timeout=1)
        except KeyboardInterrupt:
            self.running_event.clear()
            receiving_thread.join()
            streaming_thread.join()
            print("Streaming stopped by user")

        self.stop_ssh_session()




if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()

