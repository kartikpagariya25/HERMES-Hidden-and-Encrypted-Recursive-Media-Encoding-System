import zlib

MAGIC = b"HERMESIV"  # 8 bytes marker


def encode_image_into_video(uploaded_video, hidden_png) -> bytes:
    video_bytes = uploaded_video.read()
    hidden_bytes = hidden_png.read()

    if not hidden_bytes:
        raise ValueError("Hidden image is empty")

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


def decode_image_from_video(uploaded_video) -> bytes:
    data = uploaded_video.read()

    idx = data.rfind(MAGIC)
    if idx == -1:
        raise ValueError("No hidden image found")

    meta_start = idx + len(MAGIC)

    length = int.from_bytes(data[meta_start:meta_start + 4], "big")
    checksum = int.from_bytes(data[meta_start + 4:meta_start + 8], "big")
    image_bytes = data[meta_start + 8:meta_start + 8 + length]

    if len(image_bytes) != length:
        raise ValueError("Incomplete hidden image data")

    if zlib.crc32(image_bytes) != checksum:
        raise ValueError("Hidden image corrupted")

    return image_bytes
