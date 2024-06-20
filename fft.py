import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import paramiko
import threading
from datetime import date
import os
import getpass
import platform
import numpy as np


class FFTApp:
    def __init__(self, cap, fft_label):
        self.cap = cap
        self.fft_label = fft_label
        self.running_flag = False
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            self.running_flag = True
        self.thread = threading.Thread(target=self.update_fft)
        self.thread.start()

    def stop(self):
        with self.lock:
            self.running_flag = False
        self.thread.join()

    def running(self):
        with self.lock:
            return self.running_flag

    def update_fft(self):
        while self.running():
            self.apply_fft()
            cv2.waitKey(500)  # Replace with a safe delay

    def apply_fft(self):
        with self.lock:
            if not self.running_flag:
                return

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

                # Updating the GUI in a thread-safe manner
                self.fft_label.after(0, self.update_gui, magnitude_spectrum)
            else:
                print("No image captured to apply FFT.")
                self.stop()

    def update_gui(self, magnitude_spectrum):
        img = Image.fromarray(magnitude_spectrum)
        imgtk = ImageTk.PhotoImage(image=img)
        self.fft_label.configure(width=400, height=400)
        self.fft_label.imgtk = imgtk
        self.fft_label.configure(image=imgtk)
