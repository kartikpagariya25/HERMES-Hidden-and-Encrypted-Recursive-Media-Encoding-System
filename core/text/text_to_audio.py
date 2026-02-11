import wave
import zlib


def encode_text_into_audio(uploaded_file, secret_text: str) -> bytes:
    if not secret_text.strip():
        raise ValueError("Hidden text is empty")

    uploaded_file.seek(0)

    with wave.open(uploaded_file, "rb") as wav:
        params = wav.getparams()
        frames = bytearray(wav.readframes(wav.getnframes()))

    data = secret_text.encode("utf-8")
    checksum = zlib.crc32(data).to_bytes(4, "big")
    length = len(data).to_bytes(4, "big")
    payload = length + checksum + data

    bits = "".join(f"{b:08b}" for b in payload)

    if len(bits) > len(frames):
        raise ValueError("Audio file too small to hold this message")

    for i in range(len(bits)):
        frames[i] = (frames[i] & 0xFE) | int(bits[i])

    output_bytes = bytearray()
    with wave.open(output_bytes := bytearray(), "wb"):
        pass

    buffer = bytearray()
    with wave.open(memory := bytearray(), "wb"):
        pass

    import io
    out = io.BytesIO()
    with wave.open(out, "wb") as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(frames)

    out.seek(0)
    return out.read()


def decode_text_from_audio(uploaded_file) -> str:
    uploaded_file.seek(0)

    with wave.open(uploaded_file, "rb") as wav:
        frames = wav.readframes(wav.getnframes())

    bits = "".join(str(frame & 1) for frame in frames)

    raw = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))

    length = int.from_bytes(raw[:4], "big")
    checksum = int.from_bytes(raw[4:8], "big")
    message = raw[8:8 + length]

    if zlib.crc32(message) != checksum:
        raise ValueError("Data integrity check failed")

    return message.decode("utf-8")
