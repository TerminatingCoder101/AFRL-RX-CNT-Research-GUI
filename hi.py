import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading

class YourClassName:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.cap = None
        self.video_label = tk.Label(root)
        self.video_label.pack()
        self.fft_label = tk.Label(root)
        self.fft_label.pack()
        self.fft_app = None
        self.video_thread = None
        self.fft_thread = None

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_preview(self):  # For manual use only
        self.running = True
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera")
            return
        self.video_label.configure(width=400, height=400)
        
        self.fft_app = FFTApp(self.cap, self.fft_label)
        
        self.video_thread = threading.Thread(target=self.update_frame)
        self.fft_thread = threading.Thread(target=self.fft_app.start)
        
        self.video_thread.start()
        self.fft_thread.start()

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
            self.root.after(10, self.update_frame)  # Schedule the next frame update

    def stop_preview(self):  # For manual use only
        self.running = False
        if self.cap:
            self.cap.release()
        if self.video_thread:
            self.video_thread.join()
        if self.fft_thread:
            self.fft_thread.join()

    def on_closing(self):
        self.stop_preview()
        self.root.destroy()

class FFTApp:
    def __init__(self, cap, fft_label):
        self.cap = cap
        self.fft_label = fft_label
        self.running = False

    def start(self):  # This should run in a separate thread
        self.running = True
        while self.running:
            # Add FFT processing code here
            pass

    def stop(self):
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = YourClassName(root)
    app.start_preview()  # Start the preview when the application starts
    root.mainloop()
