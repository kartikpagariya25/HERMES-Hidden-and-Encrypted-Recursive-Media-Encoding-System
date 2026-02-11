import zlib
import numpy as np
from PIL import Image


DELIMITER_BITS = "1111111111111110"


def _text_to_bits(text: str) -> str:
    data = text.encode("utf-8")
    checksum = zlib.crc32(data).to_bytes(4, "big")
    payload = checksum + data
    return "".join(f"{b:08b}" for b in payload) + DELIMITER_BITS


def _bits_to_text(bits: str) -> str:
    if DELIMITER_BITS not in bits:
        raise ValueError("No hidden data found")

    bits = bits.split(DELIMITER_BITS)[0]

    if len(bits) % 8 != 0:
        raise ValueError("Corrupted hidden data")

    raw = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))

    checksum = int.from_bytes(raw[:4], "big")
    message = raw[4:]

    if zlib.crc32(message) != checksum:
        raise ValueError("Data integrity check failed")

    return message.decode("utf-8")


def encode_text_into_image(uploaded_file, secret_text: str) -> Image.Image:
    if not secret_text.strip():
        raise ValueError("Hidden text is empty")

    uploaded_file.seek(0)
    image = Image.open(uploaded_file).convert("RGB")
    data = np.array(image)

    bits = _text_to_bits(secret_text)
    capacity = data.size

    if len(bits) > capacity:
        raise ValueError("Image too small to hold this message")

    idx = 0
    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            for ch in range(3):
                if idx < len(bits):
                    data[row, col, ch] = (data[row, col, ch] & 0xFE) | int(bits[idx])
                    idx += 1

    return Image.fromarray(data)


def decode_text_from_image(uploaded_file) -> str:
    uploaded_file.seek(0)
    image = Image.open(uploaded_file).convert("RGB")
    data = np.array(image)

    bits = ""
    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            for ch in range(3):
                bits += str(data[row, col, ch] & 1)

    return _bits_to_text(bits)
