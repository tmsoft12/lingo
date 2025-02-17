import socket
import pyaudio
import threading

# Ses ayarları
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512  # Küçük buffer boyutu
WIDTH = 2

# PyAudio stream setup
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def record_and_send():
    while True:
        data = stream.read(CHUNK)  # Mikrofonla ses kaydet
        client_socket.sendto(data, ('192.168.100.7', 12345))  # Veriyi server’a gönder

# Client thread başlat
thread = threading.Thread(target=record_and_send)
thread.start()
