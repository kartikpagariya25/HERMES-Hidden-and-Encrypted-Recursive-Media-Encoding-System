import base64
import zlib

ZW_ZERO = "\u200B"
ZW_ONE = "\u200C"
ZW_MARK = "\u200D"


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


def encode_audio_into_text(cover_text: str, hidden_audio) -> str:
    if not cover_text.strip():
        raise ValueError("Cover text cannot be empty")

    hidden_audio.seek(0)
    audio_bytes = hidden_audio.read()
    if not audio_bytes:
        raise ValueError("Hidden audio is empty")

    checksum = zlib.crc32(audio_bytes)
    payload = checksum.to_bytes(4, "big") + audio_bytes
    encoded = base64.b64encode(payload)

    zw_payload = _bytes_to_zw(encoded)

    return cover_text.rstrip() + ZW_MARK + zw_payload


def decode_audio_from_text(text_data: str) -> bytes:
    if ZW_MARK not in text_data:
        raise ValueError("No hidden audio found")

    zw_payload = text_data.split(ZW_MARK, -1)[-1]
    encoded = _zw_to_bytes(zw_payload)

    raw = base64.b64decode(encoded)
    checksum = int.from_bytes(raw[:4], "big")
    audio_bytes = raw[4:]

    if zlib.crc32(audio_bytes) != checksum:
        raise ValueError("Hidden audio corrupted")

    return audio_bytes
