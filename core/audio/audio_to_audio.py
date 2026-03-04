import wave
import zlib
import io


def encode_audio_into_audio(cover_audio, hidden_audio) -> bytes:
    cover_audio.seek(0)
    hidden_audio.seek(0)
    
    hidden_bytes = hidden_audio.read()
    if not hidden_bytes:
        raise ValueError("Hidden audio is empty")
        
    with wave.open(cover_audio, "rb") as wav:
        params = wav.getparams()
        frames = bytearray(wav.readframes(wav.getnframes()))
        
    checksum = zlib.crc32(hidden_bytes).to_bytes(4, "big")
    length = len(hidden_bytes).to_bytes(4, "big")
    payload = length + checksum + hidden_bytes
    
    bits = "".join(f"{b:08b}" for b in payload)
    
    if len(bits) > len(frames):
        raise ValueError("Cover audio file too small to hold this hidden audio")
        
    for i in range(len(bits)):
        frames[i] = (frames[i] & 0xFE) | int(bits[i])
        
    out = io.BytesIO()
    with wave.open(out, "wb") as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(frames)
        
    out.seek(0)
    return out.read()


def decode_audio_from_audio(stego_audio) -> bytes:
    stego_audio.seek(0)
    
    with wave.open(stego_audio, "rb") as wav:
        frames = wav.readframes(wav.getnframes())
        
    # First extract 64 bits to find length and checksum
    if len(frames) < 64:
        raise ValueError("Audio file too short to contain hidden data")
        
    bits = "".join(str(frame & 1) for frame in frames)
    
    header_bits = bits[:64]
    header_bytes = bytes(int(header_bits[i:i+8], 2) for i in range(0, 64, 8))
    
    length = int.from_bytes(header_bytes[:4], "big")
    checksum = int.from_bytes(header_bytes[4:8], "big")
    
    total_bits = 64 + length * 8
    if len(bits) < total_bits:
        raise ValueError("Incomplete hidden data (Audio file might be truncated or corrupted)")
        
    payload_bits = bits[64:total_bits]
    hidden_bytes = bytes(int(payload_bits[i:i+8], 2) for i in range(0, len(payload_bits), 8))
    
    if len(hidden_bytes) != length:
        raise ValueError("Incomplete hidden audio data")
        
    if zlib.crc32(hidden_bytes) != checksum:
        raise ValueError("Hidden audio corrupted (checksum mismatch)")
        
    return hidden_bytes
