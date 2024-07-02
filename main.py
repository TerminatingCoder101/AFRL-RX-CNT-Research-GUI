import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk, ImageOps
import paramiko
import threading
from threading import Thread, Event
from datetime import date
import os
import getpass
import platform
import numpy as np
import time
import subprocess
import socket
import io

# Some necessary globals :)
counter = 1
file_name = ""
shutter_speed = 0
iso = 0
experiment_name = "Test"
folder_path = "Downloads/AFRL_RX_GUI"
captimg = ""

class GUI:

    def __init__(self, root):
        counter = 1
        user1 = getpass.getuser()
        system1 = platform.system()
        self.root = root
        self.root.configure(background='light blue')
        self.root.resizable(height=True, width=True)
        self.root.title("RX GUI Control")
        self.stop_event = Event()

        # ROOT
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)

        # VIDEO FRAME
        self.video_frame = ttk.LabelFrame(root, text="Video Stream")
        self.video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_label = tk.Label(self.video_frame, bg="black", fg="white")
        self.video_label.grid(row=0, column=0, sticky="nsew")
        self.video_thread = None

        # FILE AND INFO

        self.label_frame = ttk.LabelFrame(root, text="Info")
        self.label_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.label_frame.grid_rowconfigure(4, weight=1)
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
        self.control_frame = ttk.LabelFrame(root, text="Image Control")
        self.control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid_rowconfigure(4, weight=1)
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
        self.connect_button = tk.Button(self.connection_frame, text='Connect', command=self.connect_to_raspberry_pi_helper)
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
        self.fft_var = tk.BooleanVar()
        self.fft_var.set(False)  # Set the initial state to unchecked
        self.fft_frame = ttk.LabelFrame(root, text="FFT Control")
        self.fft_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.fft_frame.grid_rowconfigure(0, weight=1)
        self.fft_frame.grid_columnconfigure(0, weight=1)
        self.fft_checkbox = tk.Checkbutton(self.fft_frame, text="Show FFT", variable=self.fft_var, command=self.toggle_fft_display)
        self.fft_checkbox.grid(row=0,padx=5, pady=5, sticky="nsew")


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

        self.video_thread = Thread(target=self.update_frame)
        self.video_thread.start()

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

    def capture_image(self): # Capturing an image and saving it in a new var.
        if self.running:
            self.video_capt_label.configure(width=400, height=400)
            self.populate_file_name_entry()
            self.captimgtk = ImageTk.PhotoImage(self.captimg)
            self.video_capt_label.imgtk = self.captimgtk
            self.video_capt_label.configure(image=self.captimgtk)
            self.save_new_image = self.captimgtk

    def populate_file_name_entry(self): # Populating the file name label/entry
        global experiment_name
        global counter
        today = date.today()
        curr_date = today.strftime("%y%m%d")
        if not self.file_name_entry.get():
            default_file_name = f"{curr_date}_{counter}_{experiment_name}.png"
            self.file_name_entry.insert(0, default_file_name)  # Insert default file name
            counter+=1
        else:
            default_file_name = f"{curr_date}_{counter}_{experiment_name}.png" 
            self.file_name_entry.delete(0, tk.END)  # Clear existing content
            self.file_name_entry.insert(0, default_file_name)  # Insert default file name
            counter+=1

    def save_image(self):
        frame_temp = self.save_new_image
        global experiment_name
        global counter
        today = date.today()

        frame = ImageTk.getimage(frame_temp) #Convert ImageTK back to PIL

        curr_date = today.strftime("%y%m%d")
        if frame != "":
            global file_name
            user = getpass.getuser()
            if platform.system() == "Windows":
                filePath = f"C:/{user}/{folder_path}"
            elif platform.system() == "Darwin":
                filePath = f"/Users/{user}/{folder_path}"

            if not os.path.exists(filePath): # Make directory if it doesn't exist
                os.makedirs(filePath)

            if not self.file_name_entry.get():
                default_file_name = f"{curr_date}_{counter}_{experiment_name}.png"
                self.file_name_entry.insert(0, default_file_name)
            file_name = self.file_name_entry.get()
            fullFilePath = os.path.join(filePath, file_name)
            frame.save(fullFilePath)
            print(f"Captured image saved as {file_name} at {filePath}") # Log captured image in serial output
            self.label_name.configure(text=f"{file_name} at {filePath}")

    def save_iso_ss(self):
        global shutter_speed
        global iso
        shutter_speed = self.ss_entry.get()
        iso = self.iso_entry.get()
        print(f"Shutter Speed saved: {shutter_speed}")
        print(f"ISO saved: {iso}")

    ################################### RPI SETUP ##################################        
    
    def connect_to_raspberry_pi_helper(self):
        global shutter_speed
        global iso
        self.ip = self.ip_entry.get() #200.10.10.2
        self.user = self.user_entry.get() #pi
        self.password = self.pass_entry.get() #nanotube
        self.stream = self.connect_to_raspberry_pi(self.ip,self.user,self.password)   
    
    def connect_to_raspberry_pi(self, ip, user, password):
        global shutter_speed
        global iso
        
        self.running = False
        self.ssh_client = None

        print("Connecting to Raspberry Pi")
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(ip, username=user, password=password)
            print("Connected to Raspberry Pi")
            self.start_raspberry_pi_camera_stream(ip, user, password)
        except Exception as e:
            print(f"Failed to connect to Raspberry Pi: {e}")

    ################################### RPI CAMERA ##################################    

    def start_raspberry_pi_camera_stream(self, ip, user, password):
        self.running = True
        self.video_label.configure(width=400, height=400)
        self.stop_event.clear()
        try:
            ssh_command = f"sudo fuser -k /dev/video0"
            self.ssh_client.exec_command(ssh_command)
            print("Removed prior cams")
            ssh_command = f"python3 /home/pi/stream2.py 200.10.10.1"
            self.ssh_client.exec_command(ssh_command)
            print("Executed Stream Command")
        except Exception as e:
            print(f"Failed to start streaming script on Raspberry Pi: {e}")
        self.setup_udp_socket() # Set up sockets
        self.update_raspberry_pi_frame() # Start raspberry pi frame streams

    def setup_udp_socket(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(1)  # Set a timeout of 1 second
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        self.udp_socket.bind(('', 8000))
        print("Socket setup complete")

    def update_raspberry_pi_frame(self):
        def update_frame():
            if self.running:
                try:
                    data, _ = self.udp_socket.recvfrom(65536)
                    image = Image.open(io.BytesIO(data))
                    self.captimg = image
                    if image is not None:
                        imgtk = ImageTk.PhotoImage(image=image)
                        self.video_label.imgtk = imgtk
                        self.video_label.configure(image=imgtk)
                        if self.fft_var.get():
                            self.perform_fft(image)
                except Exception as e:
                    print(f"Failed to update frame from Raspberry Pi Camera: {e} -- Trying again.")
                    self.running = False
                self.video_label.after(10, update_frame) # If it doesn't work try again.
            else:
                self.start_raspberry_pi_camera_stream(self.ip, self.user,self.password)
                # If the entire stream disconnects, restart the stream and connections
        update_frame() # Start loop

    ################################### FFT Methods ####################################

    def toggle_fft_display(self):
        if self.fft_var.get():
            self.fft_frame.grid_rowconfigure(1, weight=1)
            self.fft_label = tk.Label(self.fft_frame, bg="black", fg="white")
            self.fft_label.grid(row=0, padx=5, pady=5, sticky="nsew")
            self.fft_checkbox.grid(row=1, padx=5, pady=5, sticky="nsew")
        else:
            self.fft_frame.grid_rowconfigure(0, weight=1)
            self.fft_label.destroy()
            self.fft_checkbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def perform_fft(self, image): # FFT Function 
        if image is not None:

            gray_image = ImageOps.grayscale(image)

            img_array = np.array(gray_image)

            dft = cv2.dft(np.float32(img_array), flags=cv2.DFT_COMPLEX_OUTPUT)
            dft_shift = np.fft.fftshift(dft)
            magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))

            cv2.normalize(magnitude_spectrum, magnitude_spectrum, 0, 255, cv2.NORM_MINMAX)
            magnitude_spectrum = np.uint8(magnitude_spectrum)
            img = Image.fromarray(magnitude_spectrum)
            imgtk = ImageTk.PhotoImage(image=img)

            self.fft_frame.grid_rowconfigure(1, weight=1)
            self.fft_label.grid(row=0, padx=5, pady=5, sticky="nsew")
            self.fft_checkbox.grid(row=1, padx=5, pady=5, sticky="nsew")
            self.fft_label.configure(width=400, height=250)
            self.fft_label.imgtk = imgtk
            self.fft_label.configure(image=imgtk)
        else:
            print("No image captured to apply FFT.")
            self.update_frame()

    def close(self): # Close all threads / roots
        if self.running:
            self.running = False
            self.stop_event.set()
        if self.cap:
            self.cap.release()
        if self.ssh_client:
            self.ssh_client.close()
        if self.video_thread:
            self.video_thread.join()     
        self.root.destroy()     

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()

