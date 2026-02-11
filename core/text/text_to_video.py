import subprocess
import tempfile
import os
import zlib


TAG_KEY = "HERMES_STEGO"


def encode_text_into_video(uploaded_file, secret_text: str) -> bytes:
    if not secret_text.strip():
        raise ValueError("Hidden text is empty")

    payload = secret_text.encode("utf-8")
    checksum = zlib.crc32(payload).to_bytes(4, "big")
    length = len(payload).to_bytes(4, "big")
    hex_payload = (length + checksum + payload).hex()

    tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp_in.write(uploaded_file.read())
    tmp_in.close()

    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp_out.close()

    cmd = [
        "ffmpeg", "-y",
        "-i", tmp_in.name,
        "-map_metadata", "0",
        "-metadata", f"{TAG_KEY}={hex_payload}",
        "-movflags", "use_metadata_tags",
        "-codec", "copy",
        tmp_out.name
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    with open(tmp_out.name, "rb") as f:
        video_bytes = f.read()

    os.unlink(tmp_in.name)
    os.unlink(tmp_out.name)

    return video_bytes


def decode_text_from_video(uploaded_file) -> str:
    tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp_in.write(uploaded_file.read())
    tmp_in.close()

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", f"format_tags={TAG_KEY}",
        "-of", "default=nw=1:nk=1",
        tmp_in.name
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )

    os.unlink(tmp_in.name)

    hex_payload = result.stdout.strip()
    if not hex_payload:
        raise ValueError("No hidden data found")

    raw = bytes.fromhex(hex_payload)
    length = int.from_bytes(raw[:4], "big")
    checksum = int.from_bytes(raw[4:8], "big")
    message = raw[8:8 + length]

    if zlib.crc32(message) != checksum:
        raise ValueError("Corrupted hidden data")

    return message.decode("utf-8")
