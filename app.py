import streamlit as st
from io import BytesIO
import zlib
import base64

from core.text.text_to_text import encode_text_into_text, decode_text_from_text
from core.text.text_to_image import encode_text_into_image, decode_text_from_image
from core.text.text_to_audio import encode_text_into_audio, decode_text_from_audio
from core.text.text_to_video import encode_text_into_video, decode_text_from_video

from core.image.image_to_image import encode_image_into_image, decode_image_from_image
from core.image.image_to_video import encode_image_into_video, decode_image_from_video
from core.image.image_to_text import encode_image_into_text, decode_image_from_text
from core.image.image_to_audio import encode_image_into_audio, decode_image_from_audio

from core.audio.audio_to_audio import encode_audio_into_audio, decode_audio_from_audio
from core.audio.audio_to_image import encode_audio_into_image, decode_audio_from_image
from core.audio.audio_to_text import encode_audio_into_text, decode_audio_from_text
from core.audio.audio_to_video import encode_audio_into_video, decode_audio_from_video

from core.video.video_to_text import encode_video_into_text, decode_video_from_text
from core.video.video_to_image import encode_video_into_image, decode_video_from_image
from core.video.video_to_audio import encode_video_into_audio, decode_video_from_audio
from core.video.video_to_video import encode_video_into_video, decode_video_from_video

from crypto import (
    encrypt_with_password, decrypt_with_password,
    encrypt_with_public_key, decrypt_with_private_key,
    generate_keypair,
)

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="🛰️ HERMES", page_icon="🛰️", layout="centered")
st.title("🛰️ HERMES")
st.caption("Hidden & Encrypted Recursive Media Encoding System")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Configuration")
hidden_type  = st.sidebar.selectbox("Data to hide",  ["Text", "Image", "Audio", "Video"])
carrier_type = st.sidebar.selectbox("Carrier type",  ["Text", "Image", "Audio", "Video"])
operation    = st.sidebar.radio("Operation",          ["Encode", "Decode"])

st.sidebar.divider()
st.sidebar.header("🔐 Encryption")
enc_mode = st.sidebar.radio(
    "Encryption mode",
    ["None (no encryption)", "Password (AES-GCM)", "Keypair (RSA + AES-GCM)"],
)

if enc_mode == "Password (AES-GCM)":
    if operation == "Encode":
        pw = st.sidebar.text_input("🔑 Encryption password", type="password")
        st.session_state["enc_password"] = pw
    else:
        pw = st.sidebar.text_input("🔑 Decryption password", type="password")
        st.session_state["dec_password"] = pw

elif enc_mode == "Keypair (RSA + AES-GCM)":
    st.sidebar.markdown("---")
    if operation == "Encode":
        pub_file = st.sidebar.file_uploader("📤 Receiver's public key (.pem)", type=["pem"])
        if pub_file:
            st.session_state["enc_pub_pem"] = pub_file.read()
    else:
        priv_file = st.sidebar.file_uploader("🗝️ Your private key (.pem)", type=["pem"])
        if priv_file:
            st.session_state["dec_priv_pem"] = priv_file.read()

    st.sidebar.markdown("**Generate a new keypair**")
    if st.sidebar.button("⚙️ Generate keypair"):
        priv_pem, pub_pem = generate_keypair()
        st.session_state["generated_priv_pem"] = priv_pem
        st.session_state["generated_pub_pem"]  = pub_pem

    if "generated_priv_pem" in st.session_state and "generated_pub_pem" in st.session_state:
        st.sidebar.warning("⚠️ Download BOTH keys before leaving!", icon="⚠️")
        col1, col2 = st.sidebar.columns(2)
        col1.download_button("📥 Private key", st.session_state["generated_priv_pem"],
            "hermes_private.pem", "application/x-pem-file", use_container_width=True)
        col2.download_button("📥 Public key", st.session_state["generated_pub_pem"],
            "hermes_public.pem", "application/x-pem-file", use_container_width=True)
        st.sidebar.caption("🔐 Private = sirf apne paas | 🔓 Public = sender ko do")

# ─────────────────────────────────────────────────────────────────────────────
# Implemented pairs
# ─────────────────────────────────────────────────────────────────────────────
implemented_pairs = {
    ("Text",  "Text"),  ("Text",  "Image"), ("Text",  "Audio"), ("Text",  "Video"),
    ("Image", "Text"),  ("Image", "Image"), ("Image", "Audio"), ("Image", "Video"),
    ("Audio", "Text"),  ("Audio", "Image"), ("Audio", "Audio"), ("Audio", "Video"),
    ("Video", "Text"),  ("Video", "Image"), ("Video", "Audio"), ("Video", "Video"),
}
if (hidden_type, carrier_type) not in implemented_pairs:
    st.warning("This combination is not yet implemented.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Encryption helpers
# ─────────────────────────────────────────────────────────────────────────────
def maybe_encrypt(raw: bytes) -> bytes:
    if enc_mode == "None (no encryption)":
        return raw
    elif enc_mode == "Password (AES-GCM)":
        password = st.session_state.get("enc_password", "").strip()
        if not password:
            raise ValueError("Please enter a password in the sidebar before encoding.")
        return encrypt_with_password(raw, password)
    else:
        pub_pem = st.session_state.get("enc_pub_pem", b"")
        if not pub_pem:
            raise ValueError("Please upload the receiver's public key (.pem) in the sidebar.")
        return encrypt_with_public_key(raw, pub_pem)

def maybe_decrypt(raw: bytes) -> bytes:
    if enc_mode == "None (no encryption)":
        return raw
    elif enc_mode == "Password (AES-GCM)":
        password = st.session_state.get("dec_password", "").strip()
        if not password:
            raise ValueError("Please enter the decryption password in the sidebar.")
        return decrypt_with_password(raw, password)
    else:
        priv_pem = st.session_state.get("dec_priv_pem", b"")
        if not priv_pem:
            raise ValueError("Please upload your private key (.pem) in the sidebar.")
        return decrypt_with_private_key(raw, priv_pem)

# ─────────────────────────────────────────────────────────────────────────────
# LSB helper — used when encryption ON + image/audio carrier
# Embeds raw bytes into PNG via LSB without requiring valid PNG input
# ─────────────────────────────────────────────────────────────────────────────
def lsb_embed_raw_into_png(cover_file, hidden_bytes: bytes):
    import numpy as np
    from PIL import Image as PILImage
    cover_file.seek(0)
    cover     = PILImage.open(cover_file).convert("RGB")
    cover_arr = np.array(cover)
    checksum  = zlib.crc32(hidden_bytes)
    header    = len(hidden_bytes).to_bytes(4, "big") + checksum.to_bytes(4, "big")
    payload   = header + hidden_bytes
    bits      = "".join(f"{b:08b}" for b in payload)
    if len(bits) > cover_arr.size:
        raise ValueError("Cover PNG too small to hold the hidden data — use a larger image")
    idx = 0
    for row in range(cover_arr.shape[0]):
        for col in range(cover_arr.shape[1]):
            for ch in range(3):
                if idx < len(bits):
                    cover_arr[row, col, ch] = (cover_arr[row, col, ch] & 0xFE) | int(bits[idx])
                    idx += 1
    return PILImage.fromarray(cover_arr)

def lsb_embed_raw_into_wav(cover_file, hidden_bytes: bytes) -> bytes:
    import wave, io
    cover_file.seek(0)
    with wave.open(cover_file, "rb") as w:
        params = w.getparams()
        frames = bytearray(w.readframes(w.getnframes()))
    checksum = zlib.crc32(hidden_bytes)
    header   = len(hidden_bytes).to_bytes(4, "big") + checksum.to_bytes(4, "big")
    payload  = header + hidden_bytes
    bits     = "".join(f"{b:08b}" for b in payload)
    if len(bits) > len(frames):
        raise ValueError("Cover WAV too small to hold the hidden data — use a larger WAV file")
    for i in range(len(bits)):
        frames[i] = (frames[i] & 0xFE) | int(bits[i])
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setparams(params)
        w.writeframes(frames)
    out.seek(0)
    return out.read()

def lsb_extract_raw_from_wav(stego_file) -> bytes:
    import wave
    stego_file.seek(0)
    with wave.open(stego_file, "rb") as w:
        frames = w.readframes(w.getnframes())
    bits = "".join(str(b & 1) for b in frames)
    raw  = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    length   = int.from_bytes(raw[:4], "big")
    checksum = int.from_bytes(raw[4:8], "big")
    data     = raw[8:8+length]
    if len(data) != length:
        raise ValueError("Incomplete hidden data")
    if zlib.crc32(data) != checksum:
        raise ValueError("Hidden data corrupted (checksum mismatch)")
    return data

# ─────────────────────────────────────────────────────────────────────────────
# Fast EOF helper — for text carrier (Audio/Image/Video hidden into Text)
# ─────────────────────────────────────────────────────────────────────────────
def eof_embed_into_text(cover_text: str, hidden_bytes: bytes, magic: bytes) -> bytes:
    checksum = zlib.crc32(hidden_bytes)
    header   = len(hidden_bytes).to_bytes(4, "big") + checksum.to_bytes(4, "big")
    return cover_text.encode("utf-8") + magic + header + hidden_bytes

def eof_extract_from_text(data: bytes, magic: bytes) -> bytes:
    idx = data.rfind(magic)
    if idx == -1:
        raise ValueError("No hidden data found in this file")
    ms       = idx + len(magic)
    length   = int.from_bytes(data[ms:ms+4], "big")
    checksum = int.from_bytes(data[ms+4:ms+8], "big")
    raw      = data[ms+8:ms+8+length]
    if len(raw) != length:
        raise ValueError("Incomplete hidden data")
    if zlib.crc32(raw) != checksum:
        raise ValueError("Hidden data corrupted (checksum mismatch)")
    return raw

# ─────────────────────────────────────────────────────────────────────────────
# Encryption banner
# ─────────────────────────────────────────────────────────────────────────────
if enc_mode == "None (no encryption)":
    st.info("🔓 Encryption is OFF — hidden data is not protected.", icon="⚠️")
elif enc_mode == "Password (AES-GCM)":
    st.success("🔒 Password encryption ON — AES-256-GCM + PBKDF2", icon="🔐")
else:
    st.success("🔒 Keypair encryption ON — RSA-OAEP + AES-256-GCM", icon="🗝️")


# =============================================================================
# TEXT → TEXT
# =============================================================================
if hidden_type == "Text" and carrier_type == "Text":

    if operation == "Encode":
        cover  = st.text_area("📄 Cover Text", height=160)
        secret = st.text_area("🕵️ Hidden Text", height=120)
        if st.button("🧬 Encode"):
            try:
                enc = maybe_encrypt(secret.encode("utf-8"))
                payload_str = base64.b64encode(enc).decode() if enc_mode != "None (no encryption)" else secret
                out = encode_text_into_text(payload_str, cover)
                st.download_button("📥 Download .txt", out, "hermes_text.txt", "text/plain")
            except Exception as e:
                st.error(str(e))
    else:
        file = st.file_uploader("📂 Upload .txt", type=["txt"])
        if st.button("🔍 Decode"):
            try:
                extracted = decode_text_from_text(file.read().decode())
                if enc_mode != "None (no encryption)":
                    dec = maybe_decrypt(base64.b64decode(extracted))
                    st.text_area("🕵️ Hidden Message", dec.decode("utf-8"), height=120)
                else:
                    st.text_area("🕵️ Hidden Message", extracted, height=120)
            except Exception as e:
                st.error(str(e))


# =============================================================================
# TEXT → IMAGE
# =============================================================================
elif hidden_type == "Text" and carrier_type == "Image":

    if operation == "Encode":
        img    = st.file_uploader("🖼️ Upload Image", type=["png", "jpg", "jpeg"])
        secret = st.text_area("🕵️ Hidden Text", height=120)
        if st.button("🧬 Encode"):
            try:
                enc = maybe_encrypt(secret.encode("utf-8"))
                payload_str = base64.b64encode(enc).decode() if enc_mode != "None (no encryption)" else secret
                stego = encode_text_into_image(img, payload_str)
                buf = BytesIO(); stego.save(buf, format="PNG"); buf.seek(0)
                st.download_button("📥 Download Image", buf, "hermes_image.png", "image/png")
            except Exception as e:
                st.error(str(e))
    else:
        img = st.file_uploader("🖼️ Upload Stego Image", type=["png", "jpg", "jpeg"])
        if st.button("🔍 Decode"):
            try:
                extracted = decode_text_from_image(img)
                if enc_mode != "None (no encryption)":
                    dec = maybe_decrypt(base64.b64decode(extracted))
                    st.text_area("🕵️ Hidden Message", dec.decode("utf-8"), height=120)
                else:
                    st.text_area("🕵️ Hidden Message", extracted, height=120)
            except Exception as e:
                st.error(str(e))


# =============================================================================
# TEXT → AUDIO
# =============================================================================
elif hidden_type == "Text" and carrier_type == "Audio":

    if operation == "Encode":
        audio  = st.file_uploader("🎵 Upload WAV", type=["wav"])
        secret = st.text_area("🕵️ Hidden Text", height=120)
        if st.button("🧬 Encode"):
            try:
                enc = maybe_encrypt(secret.encode("utf-8"))
                payload_str = base64.b64encode(enc).decode() if enc_mode != "None (no encryption)" else secret
                out = encode_text_into_audio(audio, payload_str)
                st.download_button("📥 Download WAV", out, "hermes_audio.wav", "audio/wav")
            except Exception as e:
                st.error(str(e))
    else:
        audio = st.file_uploader("🎵 Upload Stego WAV", type=["wav"])
        if st.button("🔍 Decode"):
            try:
                extracted = decode_text_from_audio(audio)
                if enc_mode != "None (no encryption)":
                    dec = maybe_decrypt(base64.b64decode(extracted))
                    st.text_area("🕵️ Hidden Message", dec.decode("utf-8"), height=120)
                else:
                    st.text_area("🕵️ Hidden Message", extracted, height=120)
            except Exception as e:
                st.error(str(e))


# =============================================================================
# TEXT → VIDEO
# =============================================================================
elif hidden_type == "Text" and carrier_type == "Video":

    if operation == "Encode":
        video  = st.file_uploader("🎬 Upload MP4 Video", type=["mp4"])
        secret = st.text_area("🕵️ Hidden Text", height=120)
        if st.button("🧬 Encode"):
            try:
                if not video: raise ValueError("Video file required")
                enc = maybe_encrypt(secret.encode("utf-8"))
                payload_str = base64.b64encode(enc).decode() if enc_mode != "None (no encryption)" else secret
                out = encode_text_into_video(video, payload_str)
                st.download_button("📥 Download Stego Video", out, "hermes_video_stego.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))
    else:
        video = st.file_uploader("🎬 Upload Stego MP4", type=["mp4"])
        if st.button("🔍 Decode"):
            try:
                if not video: raise ValueError("Video file required")
                extracted = decode_text_from_video(video)
                if enc_mode != "None (no encryption)":
                    dec = maybe_decrypt(base64.b64decode(extracted))
                    st.text_area("🕵️ Hidden Message", dec.decode("utf-8"), height=120)
                else:
                    st.text_area("🕵️ Hidden Message", extracted, height=120)
            except Exception as e:
                st.error(str(e))


# =============================================================================
# IMAGE → IMAGE
# =============================================================================
elif hidden_type == "Image" and carrier_type == "Image":

    if operation == "Encode":
        cover_img  = st.file_uploader("🖼️ Upload Cover Image (PNG only)", type=["png"])
        hidden_img = st.file_uploader("🕵️ Upload Hidden Image (PNG only)", type=["png"])
        if st.button("🧬 Encode Image into Image"):
            try:
                if not cover_img or not hidden_img:
                    raise ValueError("Both cover and hidden PNG images are required")
                enc_bytes = maybe_encrypt(hidden_img.read())
                if enc_mode != "None (no encryption)":
                    stego = lsb_embed_raw_into_png(cover_img, enc_bytes)
                else:
                    stego = encode_image_into_image(cover_png=cover_img, hidden_png=BytesIO(enc_bytes))
                st.success("✅ Hidden image embedded successfully")
                buf = BytesIO(); stego.save(buf, format="PNG"); buf.seek(0)
                st.download_button("📥 Download Stego PNG", buf, "hermes_image_stego.png", "image/png")
            except Exception as e:
                st.error(f"❌ {e}")
    else:
        stego_img = st.file_uploader("🖼️ Upload Stego Image (PNG only)", type=["png"])
        if st.button("🔍 Decode Hidden Image"):
            try:
                if not stego_img: raise ValueError("Stego PNG image required")
                raw = decode_image_from_image(stego_img)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden image extracted")
                st.download_button("📥 Download Hidden Image", dec, "hidden_image.png", "image/png")
            except Exception as e:
                st.error(f"❌ {e}")


# =============================================================================
# IMAGE → VIDEO
# =============================================================================
elif hidden_type == "Image" and carrier_type == "Video":

    if operation == "Encode":
        video      = st.file_uploader("🎬 Upload Video (MP4 / MKV / AVI)", type=["mp4", "mkv", "avi"])
        hidden_img = st.file_uploader("🕵️ Upload Hidden Image (PNG only)", type=["png"])
        if st.button("🧬 Encode Image into Video"):
            try:
                if not video or not hidden_img: raise ValueError("Video and PNG image are required")
                enc_bytes = maybe_encrypt(hidden_img.read())
                out = encode_image_into_video(video, BytesIO(enc_bytes))
                st.download_button("📥 Download Stego Video", out, "hermes_image_video.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))
    else:
        video = st.file_uploader("🎬 Upload Stego Video", type=["mp4", "mkv", "avi"])
        if st.button("🔍 Decode Hidden Image"):
            try:
                if not video: raise ValueError("Stego video required")
                raw = decode_image_from_video(video)
                dec = maybe_decrypt(raw)
                st.download_button("📥 Download Hidden Image", dec, "hidden_image.png", "image/png")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# IMAGE → TEXT  (fast EOF — zero-width too slow/RAM-heavy for images)
# =============================================================================
elif hidden_type == "Image" and carrier_type == "Text":

    MAGIC_IT = b"HERMESITX"

    if operation == "Encode":
        cover_text = st.text_area("📄 Cover Text", height=180)
        hidden_img = st.file_uploader("🕵️ Upload Hidden Image (PNG only)", type=["png"])
        if st.button("🧬 Encode Image into Text"):
            try:
                if not cover_text or not hidden_img: raise ValueError("Cover text and PNG image are required")
                enc_bytes = maybe_encrypt(hidden_img.read())
                out_bytes = eof_embed_into_text(cover_text, enc_bytes, MAGIC_IT)
                st.success("✅ Image embedded into text")
                st.download_button("📥 Download Stego File", out_bytes, "hermes_image_text.txt", "application/octet-stream")
            except Exception as e:
                st.error(str(e))
    else:
        stego_text = st.file_uploader("📂 Upload Stego Text File", type=["txt"])
        if st.button("🔍 Decode Hidden Image"):
            try:
                if not stego_text: raise ValueError("Stego text file required")
                raw = eof_extract_from_text(stego_text.read(), MAGIC_IT)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden image extracted")
                st.download_button("📥 Download Hidden Image", dec, "hidden_image.png", "image/png")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# IMAGE → AUDIO
# =============================================================================
elif hidden_type == "Image" and carrier_type == "Audio":

    if operation == "Encode":
        audio      = st.file_uploader("🎵 Upload Cover Audio (WAV only)", type=["wav"])
        hidden_img = st.file_uploader("🕵️ Upload Hidden Image (PNG only)", type=["png"])
        if st.button("🧬 Encode Image into Audio"):
            try:
                if not audio or not hidden_img: raise ValueError("WAV audio and PNG image are required")
                enc_bytes = maybe_encrypt(hidden_img.read())
                if enc_mode != "None (no encryption)":
                    out = lsb_embed_raw_into_wav(audio, enc_bytes)
                else:
                    out = encode_image_into_audio(audio, BytesIO(enc_bytes))
                st.success("✅ Hidden image embedded into audio")
                st.download_button("📥 Download Stego Audio", out, "hermes_image_audio.wav", "audio/wav")
            except Exception as e:
                st.error(str(e))
    else:
        audio = st.file_uploader("🎵 Upload Stego Audio (WAV only)", type=["wav"])
        if st.button("🔍 Decode Hidden Image"):
            try:
                if not audio: raise ValueError("Stego WAV audio required")
                if enc_mode != "None (no encryption)":
                    raw = lsb_extract_raw_from_wav(audio)
                else:
                    raw = decode_image_from_audio(audio)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden image extracted")
                st.download_button("📥 Download Hidden Image", dec, "hidden_image.png", "image/png")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# AUDIO → AUDIO
# =============================================================================
elif hidden_type == "Audio" and carrier_type == "Audio":

    if operation == "Encode":
        cover_audio  = st.file_uploader("🎵 Upload Cover Audio (WAV only)", type=["wav"])
        hidden_audio = st.file_uploader("🕵️ Upload Hidden Audio (WAV only)", type=["wav"])
        if st.button("🧬 Encode Audio into Audio"):
            try:
                if not cover_audio or not hidden_audio: raise ValueError("Both WAV files are required")
                enc_bytes = maybe_encrypt(hidden_audio.read())
                if enc_mode != "None (no encryption)":
                    out = lsb_embed_raw_into_wav(cover_audio, enc_bytes)
                else:
                    out = encode_audio_into_audio(cover_audio, BytesIO(enc_bytes))
                st.success("✅ Hidden audio embedded successfully")
                st.download_button("📥 Download Stego Audio", out, "hermes_audio_audio.wav", "audio/wav")
            except Exception as e:
                st.error(str(e))
    else:
        stego_audio = st.file_uploader("🎵 Upload Stego Audio (WAV only)", type=["wav"])
        if st.button("🔍 Decode Hidden Audio"):
            try:
                if not stego_audio: raise ValueError("Stego WAV file required")
                if enc_mode != "None (no encryption)":
                    raw = lsb_extract_raw_from_wav(stego_audio)
                else:
                    raw = decode_audio_from_audio(stego_audio)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden audio extracted")
                st.download_button("📥 Download Hidden Audio", dec, "hidden_audio.wav", "audio/wav")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# AUDIO → IMAGE
# =============================================================================
elif hidden_type == "Audio" and carrier_type == "Image":

    if operation == "Encode":
        cover_img    = st.file_uploader("🖼️ Upload Cover Image (PNG only)", type=["png"])
        hidden_audio = st.file_uploader("🕵️ Upload Hidden Audio (WAV only)", type=["wav"])
        if st.button("🧬 Encode Audio into Image"):
            try:
                if not cover_img or not hidden_audio: raise ValueError("Both cover PNG and hidden WAV files are required")
                enc_bytes = maybe_encrypt(hidden_audio.read())
                if enc_mode != "None (no encryption)":
                    stego_image = lsb_embed_raw_into_png(cover_img, enc_bytes)
                else:
                    stego_image = encode_audio_into_image(cover_img, BytesIO(enc_bytes))
                st.success("✅ Hidden audio embedded successfully")
                buf = BytesIO(); stego_image.save(buf, format="PNG"); buf.seek(0)
                st.download_button("📥 Download Stego PNG", buf, "hermes_image_stego.png", "image/png")
            except Exception as e:
                st.error(str(e))
    else:
        stego_img = st.file_uploader("🖼️ Upload Stego Image (PNG only)", type=["png"])
        if st.button("🔍 Decode Hidden Audio"):
            try:
                if not stego_img: raise ValueError("Stego PNG image required")
                if enc_mode != "None (no encryption)":
                    raw = decode_image_from_image(stego_img)
                else:
                    raw = decode_audio_from_image(stego_img)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden audio extracted")
                st.download_button("📥 Download Hidden Audio", dec, "hidden_audio.wav", "audio/wav")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# AUDIO → TEXT  (fast EOF — zero-width too slow/RAM-heavy for audio)
# =============================================================================
elif hidden_type == "Audio" and carrier_type == "Text":

    MAGIC_AT = b"HERMESATX"

    if operation == "Encode":
        cover_text   = st.text_area("📄 Cover Text", height=180)
        hidden_audio = st.file_uploader("🕵️ Upload Hidden Audio (WAV only)", type=["wav"])
        if st.button("🧬 Encode Audio into Text"):
            try:
                if not cover_text or not hidden_audio: raise ValueError("Cover text and WAV audio are required")
                enc_bytes = maybe_encrypt(hidden_audio.read())
                out_bytes = eof_embed_into_text(cover_text, enc_bytes, MAGIC_AT)
                st.success("✅ Audio embedded into text")
                st.download_button("📥 Download Stego File", out_bytes, "hermes_text_stego.txt", "application/octet-stream")
            except Exception as e:
                st.error(str(e))
    else:
        stego_text = st.file_uploader("📂 Upload Stego Text File", type=["txt"])
        if st.button("🔍 Decode Hidden Audio"):
            try:
                if not stego_text: raise ValueError("Stego text file required")
                raw = eof_extract_from_text(stego_text.read(), MAGIC_AT)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden audio extracted")
                st.download_button("📥 Download Hidden Audio", dec, "hidden_audio.wav", "audio/wav")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# AUDIO → VIDEO
# =============================================================================
elif hidden_type == "Audio" and carrier_type == "Video":

    if operation == "Encode":
        video        = st.file_uploader("🎬 Upload Video (MP4 / MKV / AVI)", type=["mp4", "mkv", "avi"])
        hidden_audio = st.file_uploader("🕵️ Upload Hidden Audio (WAV only)", type=["wav"])
        if st.button("🧬 Encode Audio into Video"):
            try:
                if not video or not hidden_audio: raise ValueError("Video and WAV audio are required")
                enc_bytes = maybe_encrypt(hidden_audio.read())
                out = encode_audio_into_video(video, BytesIO(enc_bytes))
                st.success("✅ Hidden audio embedded into video")
                st.download_button("📥 Download Stego Video", out, "hermes_video_stego.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))
    else:
        video = st.file_uploader("🎬 Upload Stego Video", type=["mp4", "mkv", "avi"])
        if st.button("🔍 Decode Hidden Audio"):
            try:
                if not video: raise ValueError("Stego video required")
                raw = decode_audio_from_video(video)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden audio extracted")
                st.download_button("📥 Download Hidden Audio", dec, "hidden_audio.wav", "audio/wav")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# VIDEO → TEXT  (fast EOF)
# =============================================================================
elif hidden_type == "Video" and carrier_type == "Text":

    MAGIC_VT = b"HERMESVTX"

    if operation == "Encode":
        cover_text   = st.text_area("📄 Cover Text", height=180)
        hidden_video = st.file_uploader("🕵️ Upload Hidden Video", type=["mp4", "mkv", "avi"])
        if st.button("🧬 Encode Video into Text"):
            try:
                if not cover_text or not hidden_video: raise ValueError("Cover text and video are required")
                enc_bytes = maybe_encrypt(hidden_video.read())
                out_bytes = eof_embed_into_text(cover_text, enc_bytes, MAGIC_VT)
                st.success("✅ Video embedded into text")
                st.download_button("📥 Download Stego File", out_bytes, "hermes_video_text.txt", "application/octet-stream")
            except Exception as e:
                st.error(str(e))
    else:
        stego_file = st.file_uploader("📂 Upload Stego Text File", type=["txt"])
        if st.button("🔍 Decode Hidden Video"):
            try:
                if not stego_file: raise ValueError("Stego file required")
                raw = eof_extract_from_text(stego_file.read(), MAGIC_VT)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden video extracted")
                st.download_button("📥 Download Hidden Video", dec, "hidden_video.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# VIDEO → IMAGE  (fast EOF)
# =============================================================================
elif hidden_type == "Video" and carrier_type == "Image":

    if operation == "Encode":
        cover_img    = st.file_uploader("🖼️ Upload Cover Image (PNG only)", type=["png"])
        hidden_video = st.file_uploader("🕵️ Upload Hidden Video", type=["mp4", "mkv", "avi"])
        if st.button("🧬 Encode Video into Image"):
            try:
                if not cover_img or not hidden_video: raise ValueError("Cover PNG and hidden video are required")
                enc_bytes = maybe_encrypt(hidden_video.read())
                out_bytes = encode_video_into_image(cover_img, BytesIO(enc_bytes))
                st.success("✅ Video embedded into image")
                st.download_button("📥 Download Stego PNG", out_bytes, "hermes_video_image.png", "application/octet-stream")
            except Exception as e:
                st.error(str(e))
    else:
        stego_img = st.file_uploader("🖼️ Upload Stego Image (PNG only)", type=["png"])
        if st.button("🔍 Decode Hidden Video"):
            try:
                if not stego_img: raise ValueError("Stego PNG required")
                raw = decode_video_from_image(stego_img)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden video extracted")
                st.download_button("📥 Download Hidden Video", dec, "hidden_video.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# VIDEO → AUDIO  (fast EOF)
# =============================================================================
elif hidden_type == "Video" and carrier_type == "Audio":

    if operation == "Encode":
        cover_audio  = st.file_uploader("🎵 Upload Cover Audio (WAV only)", type=["wav"])
        hidden_video = st.file_uploader("🕵️ Upload Hidden Video", type=["mp4", "mkv", "avi"])
        if st.button("🧬 Encode Video into Audio"):
            try:
                if not cover_audio or not hidden_video: raise ValueError("Cover WAV and hidden video are required")
                enc_bytes = maybe_encrypt(hidden_video.read())
                out_bytes = encode_video_into_audio(cover_audio, BytesIO(enc_bytes))
                st.success("✅ Video embedded into audio")
                st.download_button("📥 Download Stego WAV", out_bytes, "hermes_video_audio.wav", "application/octet-stream")
            except Exception as e:
                st.error(str(e))
    else:
        stego_audio = st.file_uploader("🎵 Upload Stego Audio (WAV only)", type=["wav"])
        if st.button("🔍 Decode Hidden Video"):
            try:
                if not stego_audio: raise ValueError("Stego WAV required")
                raw = decode_video_from_audio(stego_audio)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden video extracted")
                st.download_button("📥 Download Hidden Video", dec, "hidden_video.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# VIDEO → VIDEO  (fast EOF)
# =============================================================================
elif hidden_type == "Video" and carrier_type == "Video":

    if operation == "Encode":
        cover_video  = st.file_uploader("🎬 Upload Cover Video (MP4)", type=["mp4", "mkv", "avi"])
        hidden_video = st.file_uploader("🕵️ Upload Hidden Video (MP4)", type=["mp4", "mkv", "avi"])
        if st.button("🧬 Encode Video into Video"):
            try:
                if not cover_video or not hidden_video: raise ValueError("Both cover and hidden video files are required")
                enc_bytes = maybe_encrypt(hidden_video.read())
                out = encode_video_into_video(cover_video, BytesIO(enc_bytes))
                st.success("✅ Hidden video embedded successfully")
                st.download_button("📥 Download Stego Video", out, "hermes_video_stego.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))
    else:
        stego_video = st.file_uploader("🎬 Upload Stego Video", type=["mp4", "mkv", "avi"])
        if st.button("🔍 Decode Hidden Video"):
            try:
                if not stego_video: raise ValueError("Stego video required")
                raw = decode_video_from_video(stego_video)
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden video extracted")
                st.download_button("📥 Download Hidden Video", dec, "hidden_video.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))