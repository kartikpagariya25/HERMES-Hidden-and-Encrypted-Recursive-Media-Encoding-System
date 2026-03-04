import zlib

MAGIC = b"HERMESAV"


def encode_audio_into_video(uploaded_video, hidden_audio) -> bytes:
    uploaded_video.seek(0)
    hidden_audio.seek(0)
    
    video_bytes = uploaded_video.read()
    hidden_bytes = hidden_audio.read()

    if not hidden_bytes:
        raise ValueError("Hidden audio is empty")

    length = len(hidden_bytes).to_bytes(4, "big")
    checksum = zlib.crc32(hidden_bytes).to_bytes(4, "big")

    payload = (
        video_bytes +
        MAGIC +
        length +
        checksum +
        hidden_bytes
    )

    return payload


def decode_audio_from_video(uploaded_video) -> bytes:
    uploaded_video.seek(0)
    data = uploaded_video.read()

    idx = data.rfind(MAGIC)
    if idx == -1:
        raise ValueError("No hidden audio found")

    meta_start = idx + len(MAGIC)

    length = int.from_bytes(data[meta_start:meta_start + 4], "big")
    checksum = int.from_bytes(data[meta_start + 4:meta_start + 8], "big")
    audio_bytes = data[meta_start + 8:meta_start + 8 + length]

    if len(audio_bytes) != length:
        raise ValueError("Incomplete hidden audio data")

    if zlib.crc32(audio_bytes) != checksum:
        raise ValueError("Hidden audio corrupted")

    return audio_bytes
