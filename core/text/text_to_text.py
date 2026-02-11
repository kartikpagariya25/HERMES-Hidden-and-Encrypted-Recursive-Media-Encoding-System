import zlib

ZERO_WIDTH_MAP = {
    "00": "\u200B",
    "01": "\u200C",
    "10": "\u200D",
    "11": "\u2060"
}

REVERSE_ZERO_WIDTH_MAP = {v: k for k, v in ZERO_WIDTH_MAP.items()}


def encode_text_into_text(secret: str, carrier: str) -> str:
    if not secret.strip():
        raise ValueError("Hidden text is empty")
    if not carrier.strip():
        raise ValueError("Cover text is empty")

    secret_bytes = secret.encode("utf-8")

    length = len(secret_bytes).to_bytes(4, "big")
    checksum = zlib.crc32(secret_bytes).to_bytes(4, "big")

    payload = length + checksum + secret_bytes
    bits = "".join(f"{b:08b}" for b in payload)

    zw_sequence = "".join(
        ZERO_WIDTH_MAP[bits[i:i + 2].ljust(2, "0")]
        for i in range(0, len(bits), 2)
    )

    return carrier + "\n" + zw_sequence


def decode_text_from_text(stego: str) -> str:
    if not stego.strip():
        raise ValueError("Stego file is empty")

    bits = "".join(
        REVERSE_ZERO_WIDTH_MAP[c]
        for c in stego
        if c in REVERSE_ZERO_WIDTH_MAP
    )

    if not bits:
        raise ValueError("No hidden data found")

    if len(bits) % 8 != 0:
        raise ValueError("Corrupted hidden data")

    data = bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )

    if len(data) < 8:
        raise ValueError("Invalid payload")

    length = int.from_bytes(data[:4], "big")
    checksum = int.from_bytes(data[4:8], "big")
    hidden_bytes = data[8:8 + length]

    if len(hidden_bytes) != length:
        raise ValueError("Incomplete hidden message")

    if zlib.crc32(hidden_bytes) != checksum:
        raise ValueError("Data integrity check failed")

    return hidden_bytes.decode("utf-8")
