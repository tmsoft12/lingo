import asyncio
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, AudioStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling

class AudioReceiver:
    def __init__(self):
        self.track = None

    async def handle_track(self, track):
        print("Inside handle track")
        self.track = track
        frame_count = 0
        while True:
            try:
                print("Waiting for audio frame...")
                audio_frame = await track.recv()
                frame_count += 1
                print(f"Received audio frame {frame_count}")
                
                if isinstance(audio_frame, np.ndarray):
                    print(f"Audio frame received, length: {len(audio_frame)}")
                else:
                    print(f"Unexpected frame type: {type(audio_frame)}")
                    continue

                # Process the audio frame here (e.g., play or save)
                # For demonstration purposes, just print the frame length
                print(f"Audio Frame {frame_count}: {len(audio_frame)} samples")

            except asyncio.TimeoutError:
                print("Timeout waiting for frame, continuing...")
            except Exception as e:
                print(f"Error in handle_track: {str(e)}")
                if "Connection" in str(e):
                    break
        print("Exiting handle_track")

async def run(pc, signaling):
    await signaling.connect()

    @pc.on("track")
    def on_track(track):
        if isinstance(track, AudioStreamTrack):
            print(f"Receiving {track.kind} track")
            asyncio.ensure_future(audio_receiver.handle_track(track))

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(f"Data channel established: {channel.label}")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "connected":
            print("WebRTC connection established successfully")

    print("Waiting for offer from sender...")
    offer = await signaling.receive()
    print("Offer received")
    await pc.setRemoteDescription(offer)
    print("Remote description set")

    answer = await pc.createAnswer()
    print("Answer created")
    await pc.setLocalDescription(answer)
    print("Local description set")

    await signaling.send(pc.localDescription)
    print("Answer sent to sender")

    print("Waiting for connection to be established...")
    while pc.connectionState != "connected":
        await asyncio.sleep(0.1)

    print("Connection established, waiting for audio frames...")
    await asyncio.sleep(100)  # Wait to receive audio frames

    print("Closing connection")

async def main():
    signaling = TcpSocketSignaling("192.168.100.7", 9999)
    pc = RTCPeerConnection()
    
    global audio_receiver
    audio_receiver = AudioReceiver()

    try:
        await run(pc, signaling)
    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        print("Closing peer connection")
        await pc.close()

if __name__ == "__main__":
    asyncio.run(main())
