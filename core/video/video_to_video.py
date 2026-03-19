import zlib

MAGIC = b"HERMESVV"  # Unique magic bytes for video-in-video


def encode_video_into_video(cover_video, hidden_video) -> bytes:
    cover_video.seek(0)
    hidden_video.seek(0)

    cover_bytes = cover_video.read()
    hidden_bytes = hidden_video.read()

    if not cover_bytes:
        raise ValueError("Cover video is empty")
    if not hidden_bytes:
        raise ValueError("Hidden video is empty")

    length   = len(hidden_bytes).to_bytes(4, "big")
    checksum = zlib.crc32(hidden_bytes).to_bytes(4, "big")

    payload = (
        cover_bytes +
        MAGIC       +
        length      +
        checksum    +
        hidden_bytes
    )

    return payload


def decode_video_from_video(stego_video) -> bytes:
    stego_video.seek(0)
    data = stego_video.read()

    idx = data.rfind(MAGIC)
    if idx == -1:
        raise ValueError("No hidden video found")

    meta_start = idx + len(MAGIC)

    length      = int.from_bytes(data[meta_start:meta_start + 4], "big")
    checksum    = int.from_bytes(data[meta_start + 4:meta_start + 8], "big")
    video_bytes = data[meta_start + 8:meta_start + 8 + length]

    if len(video_bytes) != length:
        raise ValueError("Incomplete hidden video data")

    if zlib.crc32(video_bytes) != checksum:
        raise ValueError("Hidden video corrupted (checksum mismatch)")

    return video_bytes