import wave
import zlib
import audioop
import io


def _ensure_pcm(wav_file):
    wav_file.seek(0)
    with wave.open(wav_file, "rb") as w:
        params = w.getparams()
        frames = w.readframes(w.getnframes())

        # PCM formats are 1 (PCM)
        if params.comptype == "NONE":
            return params, bytearray(frames)

        # Convert non-PCM to 16-bit PCM
        width = params.sampwidth
        channels = params.nchannels

        pcm = audioop.lin2lin(frames, width, 2)
        new_params = wave._wave_params(
            channels,
            2,                      # 16-bit
            params.framerate,
            len(pcm) // (2 * channels),
            "NONE",
            "not compressed"
        )
        return new_params, bytearray(pcm)


def encode_image_into_audio(uploaded_wav, hidden_png) -> bytes:
    hidden_png.seek(0)
    image_bytes = hidden_png.read()

    if not image_bytes:
        raise ValueError("Hidden image is empty")

    length = len(image_bytes)
    checksum = zlib.crc32(image_bytes)

    payload = (
        length.to_bytes(4, "big") +
        checksum.to_bytes(4, "big") +
        image_bytes
    )

    bits = "".join(f"{b:08b}" for b in payload)

    params, frames = _ensure_pcm(uploaded_wav)

    capacity = len(frames)
    if len(bits) > capacity:
        raise ValueError("Audio file too small to hold hidden image")

    for i in range(len(bits)):
        frames[i] = (frames[i] & 0xFE) | int(bits[i])

    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setparams(params)
        w.writeframes(frames)

    out.seek(0)
    return out.read()


def decode_image_from_audio(uploaded_wav) -> bytes:
    uploaded_wav.seek(0)
    with wave.open(uploaded_wav, "rb") as w:
        frames = w.readframes(w.getnframes())

    bits = "".join(str(b & 1) for b in frames)

    raw = bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )

    length = int.from_bytes(raw[:4], "big")
    checksum = int.from_bytes(raw[4:8], "big")
    image_bytes = raw[8:8 + length]

    if len(image_bytes) != length:
        raise ValueError("Incomplete hidden image data")

    if zlib.crc32(image_bytes) != checksum:
        raise ValueError("Hidden image corrupted")

    return image_bytes
