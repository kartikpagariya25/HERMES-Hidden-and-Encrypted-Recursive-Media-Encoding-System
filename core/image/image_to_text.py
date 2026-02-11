import base64
import zlib

ZW_ZERO = "\u200B"  # bit 0
ZW_ONE = "\u200C"   # bit 1
ZW_MARK = "\u200D"  # internal separator (invisible)


def _bytes_to_zw(data: bytes) -> str:
    bits = "".join(f"{b:08b}" for b in data)
    return "".join(ZW_ONE if bit == "1" else ZW_ZERO for bit in bits)


def _zw_to_bytes(text: str) -> bytes:
    bits = []
    for ch in text:
        if ch == ZW_ONE:
            bits.append("1")
        elif ch == ZW_ZERO:
            bits.append("0")

    bit_string = "".join(bits)
    if len(bit_string) % 8 != 0:
        raise ValueError("Corrupted hidden data")

    return bytes(
        int(bit_string[i:i + 8], 2)
        for i in range(0, len(bit_string), 8)
    )


def encode_image_into_text(cover_text: str, hidden_png) -> str:
    if not cover_text.strip():
        raise ValueError("Cover text cannot be empty")

    hidden_png.seek(0)
    image_bytes = hidden_png.read()
    if not image_bytes:
        raise ValueError("Hidden image is empty")

    checksum = zlib.crc32(image_bytes)
    payload = checksum.to_bytes(4, "big") + image_bytes
    encoded = base64.b64encode(payload)

    zw_payload = _bytes_to_zw(encoded)

    # IMPORTANT: no newline, no visible marker
    return cover_text.rstrip() + ZW_MARK + zw_payload


def decode_image_from_text(text_data: str) -> bytes:
    if ZW_MARK not in text_data:
        raise ValueError("No hidden image found")

    zw_payload = text_data.split(ZW_MARK, 1)[1]
    encoded = _zw_to_bytes(zw_payload)

    raw = base64.b64decode(encoded)
    checksum = int.from_bytes(raw[:4], "big")
    image_bytes = raw[4:]

    if zlib.crc32(image_bytes) != checksum:
        raise ValueError("Hidden image corrupted")

    return image_bytes
