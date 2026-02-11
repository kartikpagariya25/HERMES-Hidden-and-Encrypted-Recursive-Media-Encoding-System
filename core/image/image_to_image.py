import zlib
import numpy as np
from PIL import Image


def encode_image_into_image(cover_png, hidden_png) -> Image.Image:
    cover_png.seek(0)
    hidden_png.seek(0)

    cover = Image.open(cover_png)
    hidden = Image.open(hidden_png)

    if cover.format != "PNG":
        raise ValueError("Cover image must be PNG")
    if hidden.format != "PNG":
        raise ValueError("Hidden image must be PNG")

    cover = cover.convert("RGB")
    hidden_bytes = hidden_png.getvalue()

    payload_len = len(hidden_bytes)
    checksum = zlib.crc32(hidden_bytes)

    header = payload_len.to_bytes(4, "big") + checksum.to_bytes(4, "big")
    payload = header + hidden_bytes

    bits = "".join(f"{b:08b}" for b in payload)

    cover_arr = np.array(cover)
    capacity = cover_arr.size

    if len(bits) > capacity:
        raise ValueError("Cover PNG too small to hold hidden image")

    idx = 0
    for row in range(cover_arr.shape[0]):
        for col in range(cover_arr.shape[1]):
            for ch in range(3):
                if idx < len(bits):
                    cover_arr[row, col, ch] = (cover_arr[row, col, ch] & 0xFE) | int(bits[idx])
                    idx += 1

    return Image.fromarray(cover_arr)


def decode_image_from_image(stego_png) -> bytes:
    stego_png.seek(0)
    image = Image.open(stego_png)

    if image.format != "PNG":
        raise ValueError("Stego image must be PNG")

    arr = np.array(image.convert("RGB"))
    bits = "".join(str(arr[row, col, ch] & 1)
                   for row in range(arr.shape[0])
                   for col in range(arr.shape[1])
                   for ch in range(3))

    raw = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))

    length = int.from_bytes(raw[:4], "big")
    checksum = int.from_bytes(raw[4:8], "big")
    data = raw[8:8 + length]

    if len(data) != length:
        raise ValueError("Incomplete hidden image data")

    if zlib.crc32(data) != checksum:
        raise ValueError("Hidden image corrupted")

    return data
