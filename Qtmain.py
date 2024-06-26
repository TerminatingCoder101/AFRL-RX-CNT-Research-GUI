import sys
import os
import cv2
import paramiko
import threading
import platform
import getpass
import numpy as np
from datetime import date
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QFileDialog)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, pyqtSignal, Qt


counter = 1
file_name = ""
shutter_speed = 0
iso = 0
experiment_name = "Hi"
folder_path = "Downloads/AFRL_RX_GUI"



class GUI(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("RX GUI Control")
        self.setGeometry(50, 50, 1200, 1200)

        self.user1 = getpass.getuser()
        self.system1 = platform.system()

        # Widgets
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(400, 400)
        self.captured_label = QLabel(self)
        self.captured_label.setFixedSize(400, 400)
        self.fft_label = QLabel(self)
        self.fft_label.setFixedSize(400, 400)

        self.file_name_entry = QLineEdit(self)
        self.save_button2 = QPushButton("Save Image", self)
        self.save_button2.clicked.connect(self.save_image)

        self.iso_entry = QLineEdit(self)
        self.ss_entry = QLineEdit(self)
        self.save_button1 = QPushButton("Save Settings", self)
        self.save_button1.clicked.connect(self.save_iso_ss)
        self.preview_button = QPushButton("Preview", self)
        self.preview_button.clicked.connect(self.start_preview)
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_image)

        self.ip_entry = QLineEdit(self)
        self.ip_entry.setFixedSize(200,100)
        self.user_entry = QLineEdit(self)
        self.user_entry.setFixedSize(200,100)
        self.pass_entry = QLineEdit(self)
        self.pass_entry.setFixedSize(200,100)
        self.pass_entry.setEchoMode(QLineEdit.Password)
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_to_raspberry_pi)

        self.label_user = QLabel(f"User: {self.user1}", self)
        self.label_user.setFixedSize(200,100)
        self.label_system = QLabel(f"System: {self.system1}", self)
        self.label_system.setFixedSize(200,100)
        self.label_name = QLabel(self)
        self.label_name.setFixedSize(200,100)

        # Layouts
        main_layout = ()
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.video_label)
        left_layout.addWidget(self.captured_label)
        left_layout.addWidget(self.fft_label)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.create_group_box("Image Control", self.create_image_control_layout()))
        right_layout.addWidget(self.create_group_box("Info", self.create_info_layout()))
        right_layout.addWidget(self.create_group_box("Connection to RPi", self.create_connection_layout()))

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Variables
        self.cap = None
        self.ssh_client = None
        self.running = False
        self.captured_frame = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def create_group_box(self, title, layout):
        group_box = QGroupBox(title)
        group_box.setLayout(layout)
        return group_box

    def create_image_control_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.preview_button)
        layout.addWidget(self.capture_button)
        layout.addWidget(QLabel("ISO:"))
        layout.addWidget(self.iso_entry)
        layout.addWidget(QLabel("Shutter Speed:"))
        layout.addWidget(self.ss_entry)
        layout.addWidget(self.save_button1)
        return layout

    def create_info_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.label_user)
        layout.addWidget(self.label_system)
        layout.addWidget(QLabel("File Name:"))
        layout.addWidget(self.file_name_entry)
        layout.addWidget(self.save_button2)
        layout.addWidget(self.label_name)
        return layout

    def create_connection_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("IP:"))
        layout.addWidget(self.ip_entry)
        layout.addWidget(QLabel("User:"))
        layout.addWidget(self.user_entry)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.pass_entry)
        layout.addWidget(self.connect_button)
        return layout

    ################################### MANUAL CAMERA ##################################

    def start_preview(self):  # For manual use only
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera")
            return

        self.camera_thread = CameraThread(self.cap)
        self.camera_thread.frame_update.connect(self.update_frame)
        self.camera_thread.start()

    def update_frame(self, image):  # For manual use only
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        if self.camera_thread:
            self.camera_thread.stop()
        if self.cap:
            self.cap.release()
        event.accept()

    def capture_image(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.captured_frame = frame
                self.populate_file_name_entry()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                self.captured_label.setPixmap(QPixmap.fromImage(image))

    def populate_file_name_entry(self):
        global experiment_name
        global counter
        today = date.today()
        curr_date = today.strftime("%y%m%d")
        if not self.file_name_entry.text():
            default_file_name = f"{curr_date}_{counter}_{experiment_name}.png"
            self.file_name_entry.setText(default_file_name)
            counter += 1
        else:
            default_file_name = f"{curr_date}_{counter}_{experiment_name}.png"
            self.file_name_entry.setText(default_file_name)
            counter += 1

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
                filePath = f"C:/{user}/{self.folder_path}"
            elif platform.system() == "Darwin":
                filePath = f"/Users/{user}/{self.folder_path}"

            if not self.file_name_entry.text():
                default_file_name = f"{curr_date}_{counter}_{experiment_name}.png"
                self.file_name_entry.setText(default_file_name)
            file_name = self.file_name_entry.text()
            cv2.imwrite(os.path.join(filePath, file_name), frame)
            print(f"Captured image saved as {file_name} at {filePath}")
            self.label_name.setText(f"{file_name} at {filePath}")

    def save_iso_ss(self):
        global shutter_speed
        global iso
        shutter_speed = self.ss_entry.text()
        iso = self.iso_entry.text()
        print(f"Shutter Speed saved: {shutter_speed}")
        print(f"ISO saved: {iso}")

    ################################### RPi CAMERA ##################################        

    def connect_to_raspberry_pi(self):
        global shutter_speed
        global iso
        ip = self.ip_entry.text()
        user = self.user_entry.text()
        password = self.pass_entry.text()
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
        self.timer.start(5)
        threading.Thread(target=self.update_raspberry_pi_frame, args=(ip, user, password, shutter_speed, iso)).start()

    def update_raspberry_pi_frame(self, ip, user, password, shutter_speed, iso):
        try:
            local_ip = '0.0.0.0'
            local_port = 2222
            ssh_command = f"raspivid -t 0 -o - -ss {shutter_speed} -ISO {iso} | nc {local_ip} {local_port}"
            
            stdin, stdout, stderr = self.ssh_client.exec_command(ssh_command)
            time.sleep(2)
            
            self.cap = cv2.VideoCapture(f"tcp://{ip}:{local_port}")
            if not self.cap.isOpened():
                print("Failed to open capture device")
                return
            
            print("Connected to RPi Camera")
            while self.cap.isOpened() and self.running:
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                    self.video_label.setPixmap(QPixmap.fromImage(image))
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

    def closeEvent(self, event):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.ssh_client:
            self.ssh_client.close()
        event.accept()

class FFTApp:
    def __init__(self, cap, fft_label):
        self.cap = cap
        self.fft_label = fft_label
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.apply_fft).start()

    def stop(self):
        self.running = False

    def apply_fft(self):
        while self.running:
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
                img = QImage(magnitude_spectrum.data, magnitude_spectrum.shape[1], magnitude_spectrum.shape[0], QImage.Format_Grayscale8)
                pixmap = QPixmap.fromImage(img)
                self.fft_label.setPixmap(pixmap)

class CameraThread():

    frame_update = pyqtSignal(QImage)

    def __init__(self, cap):
        super().__init__()
        self.cap = cap
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                scaled_image = image.scaled(400, 400, Qt.KeepAspectRatio)  # Scale the image
                self.frame_update.emit(scaled_image)

    def stop(self):
        self.running = False
        self.wait()





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec_())
