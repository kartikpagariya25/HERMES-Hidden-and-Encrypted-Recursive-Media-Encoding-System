import zlib
import numpy as np
from PIL import Image


def encode_audio_into_image(cover_png, hidden_audio) -> Image.Image:
    cover_png.seek(0)
    hidden_audio.seek(0)

    cover = Image.open(cover_png)
    if cover.format != "PNG":
        raise ValueError("Cover image must be PNG")

    cover = cover.convert("RGB")
    hidden_bytes = hidden_audio.read()
    if not hidden_bytes:
        raise ValueError("Hidden audio is empty")

    payload_len = len(hidden_bytes)
    checksum = zlib.crc32(hidden_bytes)

    header = payload_len.to_bytes(4, "big") + checksum.to_bytes(4, "big")
    payload = header + hidden_bytes

    bits = "".join(f"{b:08b}" for b in payload)

    cover_arr = np.array(cover)
    capacity = cover_arr.size

    if len(bits) > capacity:
        raise ValueError("Cover PNG too small to hold hidden audio")

    flat_arr = cover_arr.reshape(-1)
    
    for i in range(len(bits)):
        flat_arr[i] = (flat_arr[i] & 0xFE) | int(bits[i])

    cover_arr = flat_arr.reshape(cover_arr.shape)
    return Image.fromarray(cover_arr)


def decode_audio_from_image(stego_png) -> bytes:
    stego_png.seek(0)
    image = Image.open(stego_png)

    if image.format != "PNG":
        raise ValueError("Stego image must be PNG")

    arr = np.array(image.convert("RGB")).reshape(-1)
    
    if len(arr) < 64:
        raise ValueError("Image too small to contain hidden data")

    header_bits = "".join(str(arr[i] & 1) for i in range(64))
    header_raw = bytes(int(header_bits[i:i+8], 2) for i in range(0, 64, 8))
    
    length = int.from_bytes(header_raw[:4], "big")
    checksum = int.from_bytes(header_raw[4:8], "big")
    
    total_bits = 64 + length * 8
    if len(arr) < total_bits:
        raise ValueError("Incomplete hidden data (Image too small or corrupted)")
        
    payload_bits = "".join(str(arr[i] & 1) for i in range(64, total_bits))
    hidden_bytes = bytes(int(payload_bits[i:i+8], 2) for i in range(0, len(payload_bits), 8))

    if len(hidden_bytes) != length:
        raise ValueError("Incomplete hidden audio data")

    if zlib.crc32(hidden_bytes) != checksum:
        raise ValueError("Hidden audio corrupted")

    return hidden_bytes
