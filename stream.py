from picamera2 import Picamera2
from libcamera import controls
import socket
import time
import io
import argparse

def start_stream(ip_addr, shutter_speed, iso_value):
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (400, 400)})
    iso_value = int(iso_value)
    #Set controls for Camera

    picam2.set_controls({"Contrast": 0})
    picam2.set_controls({"Brightness": 0.5})
    picam2.set_controls({"Saturation": 0})
    picam2.set_controls({"Sharpness": 0})
    picam2.set_controls({"AwbEnable": 0})
    picam2.set_controls({"AwbMode": 7})
    picam2.set_controls({"ColourGains": (1.9387,1.2723)})
    picam2.set_controls({"AeMeteringMode": controls.AeMeteringModeEnum.CentreWeighted})
    picam2.set_controls({"ExposureTime": shutter_speed})
    ag = (iso_value / 100) * 2.317
    picam2.set_controls({"AnalogueGain": ag})

    
    picam2.configure(config)
    picam2.start()

    # Set up UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(2)  # Camera warm-up time

    print("Starting camera stream...")
    try:
        while True:
            buffer = io.BytesIO()
            picam2.capture_file(buffer, format='jpeg')
            buffer.seek(0)
            client_socket.sendto(buffer.read(), (ip_addr, 8000))
            print("Frame sent")
            time.sleep(0.1)  # Adjust this as needed to control frame rate
    finally:
            picam2.stop()

if __name__ == '__main__':
    print("Script started")
    parser = argparse.ArgumentParser()
    parser.add_argument("ipaddr", help="The IP address of the local machine")
    parser.add_argument("shutter_speed", help="The shutter speed")
    parser.add_argument("iso_value", help="The iso ")
    args = parser.parse_args()
    ip_addr = args.ipaddr
    shutter_speed = args.shutter_speed
    iso_value = args.iso_value
    start_stream(ip_addr, shutter_speed, iso_value)

