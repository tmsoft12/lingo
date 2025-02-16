import asyncio
import sounddevice as sd
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, AudioStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling

class CustomAudioStreamTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()
        self.sample_rate = 44100  # Mikrofonun örnekleme hızı
        self.channels = 1  # Ses kanal sayısı (Mono)
        self.frame_count = 0

        # Mikrofon verisi için bir stream açıyoruz
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=self.channels)
        self.stream.start()

    async def recv(self):
        self.frame_count += 1
        print(f"Sending audio frame {self.frame_count}")
        # Mikrofon verisini oku
        audio_data, overflowed = self.stream.read(self.sample_rate // 30)  # 30 fps
        if overflowed:
            print("Audio overflowed, skipping frame")
            return None
        return audio_data  # Ses verisini döndür

async def setup_webrtc_and_run(ip_address, port):
    signaling = TcpSocketSignaling(ip_address, port)
    pc = RTCPeerConnection()
    audio_sender = CustomAudioStreamTrack()
    pc.addTrack(audio_sender)

    try:
        await signaling.connect()

        @pc.on("datachannel")
        def on_datachannel(channel):
            print(f"Data channel established: {channel.label}")

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"Connection state is {pc.connectionState}")
            if pc.connectionState == "connected":
                print("WebRTC connection established successfully")

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await signaling.send(pc.localDescription)

        while True:
            obj = await signaling.receive()
            if isinstance(obj, RTCSessionDescription):
                await pc.setRemoteDescription(obj)
                print("Remote description set")
            elif obj is None:
                print("Signaling ended")
                break
        print("Closing connection")
    finally:
        await pc.close()

async def main():
    ip_address = "192.168.100.7"  # IP Address of Remote Server/Machine
    port = 9999
    await setup_webrtc_and_run(ip_address, port)

if __name__ == "__main__":
    asyncio.run(main())
