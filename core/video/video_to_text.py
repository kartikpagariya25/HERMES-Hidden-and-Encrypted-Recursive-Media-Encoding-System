import zlib

MAGIC = b"HERMESVT"


def encode_video_into_text(cover_text: str, hidden_video) -> bytes:
    if not cover_text.strip():
        raise ValueError("Cover text cannot be empty")

    hidden_video.seek(0)
    video_bytes = hidden_video.read()
    if not video_bytes:
        raise ValueError("Hidden video is empty")

    checksum = zlib.crc32(video_bytes)
    header   = len(video_bytes).to_bytes(4, "big") + checksum.to_bytes(4, "big")

    return cover_text.encode("utf-8") + MAGIC + header + video_bytes


def decode_video_from_text(data) -> bytes:
    if isinstance(data, str):
        data = data.encode("utf-8")

    idx = data.rfind(MAGIC)
    if idx == -1:
        raise ValueError("No hidden video found in this file")

    ms          = idx + len(MAGIC)
    length      = int.from_bytes(data[ms:ms + 4], "big")
    checksum    = int.from_bytes(data[ms + 4:ms + 8], "big")
    video_bytes = data[ms + 8:ms + 8 + length]

    if len(video_bytes) != length:
        raise ValueError("Incomplete hidden video data")
    if zlib.crc32(video_bytes) != checksum:
        raise ValueError("Hidden video corrupted (checksum mismatch)")

    return video_bytes