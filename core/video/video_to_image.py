import zlib

MAGIC = b"HERMESVI"


def encode_video_into_image(cover_png, hidden_video) -> bytes:
    cover_png.seek(0)
    hidden_video.seek(0)

    cover_bytes = cover_png.read()
    video_bytes = hidden_video.read()

    if not cover_bytes:
        raise ValueError("Cover image is empty")
    if not video_bytes:
        raise ValueError("Hidden video is empty")

    checksum = zlib.crc32(video_bytes)
    header   = len(video_bytes).to_bytes(4, "big") + checksum.to_bytes(4, "big")

    return cover_bytes + MAGIC + header + video_bytes


def decode_video_from_image(stego_png) -> bytes:
    stego_png.seek(0)
    data = stego_png.read()

    idx = data.rfind(MAGIC)
    if idx == -1:
        raise ValueError("No hidden video found in this image")

    ms          = idx + len(MAGIC)
    length      = int.from_bytes(data[ms:ms + 4], "big")
    checksum    = int.from_bytes(data[ms + 4:ms + 8], "big")
    video_bytes = data[ms + 8:ms + 8 + length]

    if len(video_bytes) != length:
        raise ValueError("Incomplete hidden video data")
    if zlib.crc32(video_bytes) != checksum:
        raise ValueError("Hidden video corrupted (checksum mismatch)")

    return video_bytes