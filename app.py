import streamlit as st
from io import BytesIO

from core.text.text_to_text import encode_text_into_text, decode_text_from_text
from core.text.text_to_image import encode_text_into_image, decode_text_from_image
from core.text.text_to_audio import encode_text_into_audio, decode_text_from_audio
from core.text.text_to_video import encode_text_into_video, decode_text_from_video
from core.image.image_to_image import (
    encode_image_into_image,
    decode_image_from_image
)
from core.image.image_to_video import (
    encode_image_into_video,
    decode_image_from_video
)

from core.image.image_to_text import (
    encode_image_into_text,
    decode_image_from_text
)
from core.image.image_to_audio import (
    encode_image_into_audio,
    decode_image_from_audio
)
from core.audio.audio_to_audio import (
    encode_audio_into_audio,
    decode_audio_from_audio
)
from core.audio.audio_to_image import encode_audio_into_image, decode_audio_from_image
from core.audio.audio_to_text import encode_audio_into_text, decode_audio_from_text
from core.audio.audio_to_video import encode_audio_into_video, decode_audio_from_video

from core.video.video_to_text  import encode_video_into_text,  decode_video_from_text
from core.video.video_to_image import encode_video_into_image, decode_video_from_image
from core.video.video_to_audio import encode_video_into_audio, decode_video_from_audio
from core.video.video_to_video import encode_video_into_video, decode_video_from_video

from core.video.video_to_video  import encode_video_into_video,  decode_video_from_video

from crypto import (
    encrypt_with_password,   decrypt_with_password,
    encrypt_with_public_key, decrypt_with_private_key,
    generate_keypair,        decrypt_auto,
)




st.set_page_config(page_title="🛰️ HERMES", page_icon="🛰️", layout="centered")

st.title("🛰️ HERMES")
st.caption("Hidden & Encrypted Recursive Media Encoding System")

# ─────────────────────────────────────────────────────────────────────────────
# Helper: encrypt / decrypt
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

st.sidebar.header("⚙️ Configuration")
hidden_type = st.sidebar.selectbox("Data to hide", ["Text", "Image", "Audio", "Video"])
carrier_type = st.sidebar.selectbox("Carrier type", ["Text", "Image", "Audio", "Video"])
operation = st.sidebar.radio("Operation", ["Encode", "Decode"])

# ── Encryption sidebar ────────────────────────────────────────────────────────
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

implemented_pairs = {
    ("Text", "Text"),
    ("Text", "Image"),
    ("Text", "Audio"),
    ("Text", "Video"),
    ("Image", "Image"),
    ("Image", "Video"),
    ("Image", "Text"),
    ("Image", "Audio"),
    ("Audio", "Audio"),
    ("Audio", "Image"),
    ("Audio", "Text"),
    ("Audio", "Video"),
    ("Video", "Video"),
    ("Video", "Text"),
    ("Video", "Image"),
    ("Video", "Audio"),
}


if (hidden_type, carrier_type) not in implemented_pairs:
    st.warning("This combination is not yet implemented.")
    st.stop()

# Encryption banner
if enc_mode == "None (no encryption)":
    st.info("🔓 Encryption is OFF — hidden data is not protected.", icon="⚠️")
elif enc_mode == "Password (AES-GCM)":
    st.success("🔒 Password encryption ON — AES-256-GCM + PBKDF2", icon="🔐")
else:
    st.success("🔒 Keypair encryption ON — RSA-OAEP + AES-256-GCM", icon="🗝️")

# ================= TEXT → TEXT =================
if hidden_type == "Text" and carrier_type == "Text":

    if operation == "Encode":
        cover = st.text_area("📄 Cover Text", height=160)
        secret = st.text_area("🕵️ Hidden Text", height=120)

        if st.button("🧬 Encode"):
            try:
                out = encode_text_into_text(secret, cover)
                st.download_button("📥 Download .txt", out, "hermes_text.txt", "text/plain")
            except Exception as e:
                st.error(str(e))

    else:
        file = st.file_uploader("📂 Upload .txt", type=["txt"])
        if st.button("🔍 Decode"):
            try:
                st.text_area("🕵️ Hidden Message", decode_text_from_text(file.read().decode()), height=120)
            except Exception as e:
                st.error(str(e))

# ================= TEXT → IMAGE =================
elif hidden_type == "Text" and carrier_type == "Image":

    if operation == "Encode":
        img = st.file_uploader("🖼️ Upload Image", type=["png", "jpg", "jpeg"])
        secret = st.text_area("🕵️ Hidden Text", height=120)

        if st.button("🧬 Encode"):
            try:
                stego = encode_text_into_image(img, secret)
                buf = BytesIO()
                stego.save(buf, format="PNG")
                buf.seek(0)
                st.download_button("📥 Download Image", buf, "hermes_image.png", "image/png")
            except Exception as e:
                st.error(str(e))

    else:
        img = st.file_uploader("🖼️ Upload Stego Image", type=["png", "jpg", "jpeg"])
        if st.button("🔍 Decode"):
            try:
                st.text_area("🕵️ Hidden Message", decode_text_from_image(img), height=120)
            except Exception as e:
                st.error(str(e))

# ================= TEXT → AUDIO =================
elif hidden_type == "Text" and carrier_type == "Audio":

    if operation == "Encode":
        audio = st.file_uploader("🎵 Upload WAV", type=["wav"])
        secret = st.text_area("🕵️ Hidden Text", height=120)

        if st.button("🧬 Encode"):
            try:
                out = encode_text_into_audio(audio, secret)
                st.download_button("📥 Download WAV", out, "hermes_audio.wav", "audio/wav")
            except Exception as e:
                st.error(str(e))

    else:
        audio = st.file_uploader("🎵 Upload Stego WAV", type=["wav"])
        if st.button("🔍 Decode"):
            try:
                st.text_area("🕵️ Hidden Message", decode_text_from_audio(audio), height=120)
            except Exception as e:
                st.error(str(e))

# ================= TEXT → VIDEO =================
elif hidden_type == "Text" and carrier_type == "Video":

    if operation == "Encode":
        video = st.file_uploader("🎬 Upload MP4 Video", type=["mp4"])
        secret = st.text_area("🕵️ Hidden Text", height=120)

        if st.button("🧬 Encode"):
            try:
                if not video:
                    raise ValueError("Video file required")

                out = encode_text_into_video(video, secret)

                st.download_button(
                    "📥 Download Stego Video",
                    out,
                    "hermes_video_stego.mp4",
                    "video/mp4"
                )

            except Exception as e:
                st.error(str(e))

    else:
        video = st.file_uploader("🎬 Upload Stego MP4", type=["mp4"])

        if st.button("🔍 Decode"):
            try:
                if not video:
                    raise ValueError("Video file required")

                hidden = decode_text_from_video(video)
                st.text_area("🕵️ Hidden Message", hidden, height=120)

            except Exception as e:
                st.error(str(e))

# ======================================================
# IMAGE → IMAGE (PNG → PNG ONLY)
# ======================================================
elif hidden_type == "Image" and carrier_type == "Image":

    if operation == "Encode":
        cover_img = st.file_uploader(
            "🖼️ Upload Cover Image (PNG only)",
            type=["png"],
            help="Only PNG images are supported (lossless required)"
        )

        hidden_img = st.file_uploader(
            "🕵️ Upload Hidden Image (PNG only)",
            type=["png"],
            help="Only PNG images are supported (lossless required)"
        )

        if st.button("🧬 Encode Image into Image"):
            try:
                if not cover_img or not hidden_img:
                    raise ValueError("Both cover and hidden PNG images are required")

                stego_image = encode_image_into_image(
                    cover_png=cover_img,
                    hidden_png=hidden_img
                )

                st.success("✅ Hidden image embedded successfully")

                from io import BytesIO
                buf = BytesIO()
                stego_image.save(buf, format="PNG")
                buf.seek(0)

                st.download_button(
                    "📥 Download Stego PNG",
                    buf,
                    "hermes_image_stego.png",
                    "image/png"
                )

            except Exception as e:
                st.error(f"❌ {str(e)}")

    else:
        stego_img = st.file_uploader(
            "🖼️ Upload Stego Image (PNG only)",
            type=["png"],
            help="Upload the PNG generated during encoding"
        )

        if st.button("🔍 Decode Hidden Image"):
            try:
                if not stego_img:
                    raise ValueError("Stego PNG image required")

                hidden_bytes = decode_image_from_image(stego_img)

                st.success("✅ Hidden image extracted")

                st.download_button(
                    "📥 Download Hidden Image",
                    hidden_bytes,
                    "hidden_image.png",
                    "image/png"
                )

            except Exception as e:
                st.error(f"❌ {str(e)}")

# ======================================================
# IMAGE → VIDEO (METADATA-BASED, PNG ONLY)
# ======================================================
elif hidden_type == "Image" and carrier_type == "Video":

    if operation == "Encode":
        video = st.file_uploader(
            "🎬 Upload Video (MP4 / MKV / AVI)",
            type=["mp4", "mkv", "avi"],
            help="Hidden data will be appended safely after video EOF"
        )

        hidden_img = st.file_uploader(
            "🕵️ Upload Hidden Image (PNG only)",
            type=["png"]
        )

        if st.button("🧬 Encode Image into Video"):
            try:
                if not video or not hidden_img:
                    raise ValueError("Video and PNG image are required")

                out = encode_image_into_video(video, hidden_img)

                st.download_button(
                    "📥 Download Stego Video",
                    out,
                    "hermes_image_video.mp4",
                    "video/mp4"
                )

            except Exception as e:
                st.error(str(e))

    else:
        video = st.file_uploader(
            "🎬 Upload Stego Video",
            type=["mp4", "mkv", "avi"]
        )

        if st.button("🔍 Decode Hidden Image"):
            try:
                if not video:
                    raise ValueError("Stego video required")

                img_bytes = decode_image_from_video(video)

                st.download_button(
                    "📥 Download Hidden Image",
                    img_bytes,
                    "hidden_image.png",
                    "image/png"
                )

            except Exception as e:
                st.error(str(e))

# ======================================================
# IMAGE → TEXT (BASE64 + MARKERS, ROBUST)
# ======================================================
elif hidden_type == "Image" and carrier_type == "Text":

    if operation == "Encode":
        cover_text = st.text_area(
            "📄 Cover Text",
            height=180,
            help="This text will remain readable"
        )

        hidden_img = st.file_uploader(
            "🕵️ Upload Hidden Image (PNG only)",
            type=["png"]
        )

        if st.button("🧬 Encode Image into Text"):
            try:
                if not cover_text or not hidden_img:
                    raise ValueError("Cover text and PNG image are required")

                out_text = encode_image_into_text(cover_text, hidden_img)

                st.success("✅ Image embedded into text")

                st.download_button(
                    "📥 Download Stego Text",
                    out_text,
                    "hermes_image_text.txt",
                    "text/plain"
                )

            except Exception as e:
                st.error(str(e))

    else:
        stego_text = st.file_uploader(
            "📂 Upload Stego Text File",
            type=["txt"]
        )

        if st.button("🔍 Decode Hidden Image"):
            try:
                if not stego_text:
                    raise ValueError("Stego text file required")

                text_data = stego_text.read().decode("utf-8")
                image_bytes = decode_image_from_text(text_data)

                st.success("✅ Hidden image extracted")

                st.download_button(
                    "📥 Download Hidden Image",
                    image_bytes,
                    "hidden_image.png",
                    "image/png"
                )

            except Exception as e:
                st.error(str(e))

# ======================================================
# IMAGE → AUDIO (WAV ONLY)
# ======================================================
elif hidden_type == "Image" and carrier_type == "Audio":

    if operation == "Encode":
        audio = st.file_uploader(
            "🎵 Upload Cover Audio (WAV only)",
            type=["wav"],
            help="Only WAV is supported (lossless PCM required)"
        )

        hidden_img = st.file_uploader(
            "🕵️ Upload Hidden Image (PNG only)",
            type=["png"]
        )

        if st.button("🧬 Encode Image into Audio"):
            try:
                if not audio or not hidden_img:
                    raise ValueError("WAV audio and PNG image are required")

                out = encode_image_into_audio(audio, hidden_img)

                st.success("✅ Hidden image embedded into audio")

                st.download_button(
                    "📥 Download Stego Audio",
                    out,
                    "hermes_image_audio.wav",
                    "audio/wav"
                )

            except Exception as e:
                st.error(str(e))

    else:
        audio = st.file_uploader(
            "🎵 Upload Stego Audio (WAV only)",
            type=["wav"]
        )

        if st.button("🔍 Decode Hidden Image"):
            try:
                if not audio:
                    raise ValueError("Stego WAV audio required")

                image_bytes = decode_image_from_audio(audio)

                st.success("✅ Hidden image extracted")

                st.download_button(
                    "📥 Download Hidden Image",
                    image_bytes,
                    "hidden_image.png",
                    "image/png"
                )

            except Exception as e:
                st.error(str(e))

# ======================================================
# AUDIO → AUDIO (WAV → WAV)
# ======================================================
elif hidden_type == "Audio" and carrier_type == "Audio":

    if operation == "Encode":
        cover_audio = st.file_uploader(
            "🎵 Upload Cover Audio (WAV only)",
            type=["wav"],
            help="Carrier must be WAV (any variant will be normalized)"
        )

        hidden_audio = st.file_uploader(
            "🕵️ Upload Hidden Audio (WAV only)",
            type=["wav"]
        )

        if st.button("🧬 Encode Audio into Audio"):
            try:
                if not cover_audio or not hidden_audio:
                    raise ValueError("Both cover and hidden WAV files are required")

                out = encode_audio_into_audio(cover_audio, hidden_audio)

                st.success("✅ Hidden audio embedded successfully")

                st.download_button(
                    "📥 Download Stego Audio",
                    out,
                    "hermes_audio_audio.wav",
                    "audio/wav"
                )

            except Exception as e:
                st.error(str(e))

    else:
        stego_audio = st.file_uploader(
            "🎵 Upload Stego Audio (WAV only)",
            type=["wav"]
        )

        if st.button("🔍 Decode Hidden Audio"):
            try:
                if not stego_audio:
                    raise ValueError("Stego WAV file required")

                hidden_bytes = decode_audio_from_audio(stego_audio)

                st.success("✅ Hidden audio extracted")

                st.download_button(
                    "📥 Download Hidden Audio",
                    hidden_bytes,
                    "hidden_audio.wav",
                    "audio/wav"
                )

            except Exception as e:
                st.error(str(e))

# ======================================================
# AUDIO → IMAGE (WAV → PNG)
# ======================================================
elif hidden_type == "Audio" and carrier_type == "Image":

    if operation == "Encode":
        cover_img = st.file_uploader(
            "🖼️ Upload Cover Image (PNG only)",
            type=["png"]
        )
        hidden_audio = st.file_uploader(
            "🕵️ Upload Hidden Audio (WAV only)",
            type=["wav"]
        )

        if st.button("🧬 Encode Audio into Image"):
            try:
                if not cover_img or not hidden_audio:
                    raise ValueError("Both cover PNG and hidden WAV files are required")

                stego_image = encode_audio_into_image(cover_img, hidden_audio)
                st.success("✅ Hidden audio embedded successfully")

                from io import BytesIO
                buf = BytesIO()
                stego_image.save(buf, format="PNG")
                buf.seek(0)

                st.download_button(
                    "📥 Download Stego PNG",
                    buf,
                    "hermes_image_stego.png",
                    "image/png"
                )

            except Exception as e:
                st.error(str(e))

    else:
        stego_img = st.file_uploader(
            "🖼️ Upload Stego Image (PNG only)",
            type=["png"]
        )

        if st.button("🔍 Decode Hidden Audio"):
            try:
                if not stego_img:
                    raise ValueError("Stego PNG image required")

                hidden_bytes = decode_audio_from_image(stego_img)
                st.success("✅ Hidden audio extracted")

                st.download_button(
                    "📥 Download Hidden Audio",
                    hidden_bytes,
                    "hidden_audio.wav",
                    "audio/wav"
                )

            except Exception as e:
                st.error(str(e))

# ======================================================
# AUDIO → TEXT
# ======================================================
elif hidden_type == "Audio" and carrier_type == "Text":

    if operation == "Encode":
        cover_text = st.text_area(
            "📄 Cover Text",
            height=180
        )
        hidden_audio = st.file_uploader(
            "🕵️ Upload Hidden Audio (WAV only)",
            type=["wav"]
        )

        if st.button("🧬 Encode Audio into Text"):
            try:
                if not cover_text or not hidden_audio:
                    raise ValueError("Cover text and WAV audio are required")

                out_text = encode_audio_into_text(cover_text, hidden_audio)
                st.success("✅ Audio embedded into text")

                st.download_button(
                    "📥 Download Stego Text",
                    out_text,
                    "hermes_text_stego.txt",
                    "text/plain"
                )

            except Exception as e:
                st.error(str(e))

    else:
        stego_text = st.file_uploader(
            "📂 Upload Stego Text File",
            type=["txt"]
        )

        if st.button("🔍 Decode Hidden Audio"):
            try:
                if not stego_text:
                    raise ValueError("Stego text file required")

                text_data = stego_text.read().decode("utf-8")
                audio_bytes = decode_audio_from_text(text_data)
                st.success("✅ Hidden audio extracted")

                st.download_button(
                    "📥 Download Hidden Audio",
                    audio_bytes,
                    "hidden_audio.wav",
                    "audio/wav"
                )

            except Exception as e:
                st.error(str(e))

# ======================================================
# AUDIO → VIDEO
# ======================================================
elif hidden_type == "Audio" and carrier_type == "Video":

    if operation == "Encode":
        video = st.file_uploader(
            "🎬 Upload Video (MP4 / MKV / AVI)",
            type=["mp4", "mkv", "avi"]
        )
        hidden_audio = st.file_uploader(
            "🕵️ Upload Hidden Audio (WAV only)",
            type=["wav"]
        )

        if st.button("🧬 Encode Audio into Video"):
            try:
                if not video or not hidden_audio:
                    raise ValueError("Video and WAV audio are required")

                out = encode_audio_into_video(video, hidden_audio)
                st.success("✅ Hidden audio embedded into video")

                st.download_button(
                    "📥 Download Stego Video",
                    out,
                    "hermes_video_stego.mp4",
                    "video/mp4"
                )

            except Exception as e:
                st.error(str(e))

    else:
        video = st.file_uploader(
            "🎬 Upload Stego Video",
            type=["mp4", "mkv", "avi"]
        )

        if st.button("🔍 Decode Hidden Audio"):
            try:
                if not video:
                    raise ValueError("Stego video required")

                audio_bytes = decode_audio_from_video(video)
                st.success("✅ Hidden audio extracted")

                st.download_button(
                    "📥 Download Hidden Audio",
                    audio_bytes,
                    "hidden_audio.wav",
                    "audio/wav"
                )

            except Exception as e:
                st.error(str(e))


# =============================================================================
# VIDEO → TEXT  (fast — EOF appending)
# =============================================================================
elif hidden_type == "Video" and carrier_type == "Text":

    if operation == "Encode":
        cover_text   = st.text_area("📄 Cover Text", height=180)
        hidden_video = st.file_uploader("🕵️ Upload Hidden Video", type=["mp4", "mkv", "avi"])

        if st.button("🧬 Encode Video into Text"):
            try:
                if not cover_text or not hidden_video:
                    raise ValueError("Cover text and video are required")
                enc_bytes = maybe_encrypt(hidden_video.read())
                out_bytes = encode_video_into_text(cover_text, BytesIO(enc_bytes))
                st.success("✅ Video embedded into text")
                st.download_button("📥 Download Stego File", out_bytes, "hermes_video_text.txt", "application/octet-stream")
            except Exception as e:
                st.error(str(e))

    else:
        stego_file = st.file_uploader("📂 Upload Stego Text File", type=["txt"])
        if st.button("🔍 Decode Hidden Video"):
            try:
                if not stego_file: raise ValueError("Stego file required")
                raw = decode_video_from_text(stego_file.read())
                dec = maybe_decrypt(raw)
                st.success("✅ Hidden video extracted")
                st.download_button("📥 Download Hidden Video", dec, "hidden_video.mp4", "video/mp4")
            except Exception as e:
                st.error(str(e))


# =============================================================================
# VIDEO → IMAGE  (fast — EOF appending, no size limit)
# =============================================================================
elif hidden_type == "Video" and carrier_type == "Image":

    if operation == "Encode":
        cover_img    = st.file_uploader("🖼️ Upload Cover Image (PNG only)", type=["png"])
        hidden_video = st.file_uploader("🕵️ Upload Hidden Video", type=["mp4", "mkv", "avi"])

        if st.button("🧬 Encode Video into Image"):
            try:
                if not cover_img or not hidden_video:
                    raise ValueError("Cover PNG and hidden video are required")
                enc_bytes = maybe_encrypt(hidden_video.read())
                out_bytes = encode_video_into_image(cover_img, BytesIO(enc_bytes))
                st.success("✅ Video embedded into image")
                st.download_button("📥 Download Stego PNG", out_bytes, "hermes_video_image.png", "image/png")
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
# VIDEO → AUDIO  (fast — EOF appending, no size limit)
# =============================================================================
elif hidden_type == "Video" and carrier_type == "Audio":

    if operation == "Encode":
        cover_audio  = st.file_uploader("🎵 Upload Cover Audio (WAV only)", type=["wav"])
        hidden_video = st.file_uploader("🕵️ Upload Hidden Video", type=["mp4", "mkv", "avi"])

        if st.button("🧬 Encode Video into Audio"):
            try:
                if not cover_audio or not hidden_video:
                    raise ValueError("Cover WAV and hidden video are required")
                enc_bytes = maybe_encrypt(hidden_video.read())
                out_bytes = encode_video_into_audio(cover_audio, BytesIO(enc_bytes))
                st.success("✅ Video embedded into audio")
                st.download_button("📥 Download Stego WAV", out_bytes, "hermes_video_audio.wav", "audio/wav")
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
# VIDEO → VIDEO  (fast — EOF appending)
# =============================================================================
elif hidden_type == "Video" and carrier_type == "Video":

    if operation == "Encode":
        cover_video  = st.file_uploader("🎬 Upload Cover Video (MP4)", type=["mp4", "mkv", "avi"])
        hidden_video = st.file_uploader("🕵️ Upload Hidden Video (MP4)", type=["mp4", "mkv", "avi"])

        if st.button("🧬 Encode Video into Video"):
            try:
                if not cover_video or not hidden_video:
                    raise ValueError("Both cover and hidden video files are required")
                enc_bytes  = maybe_encrypt(hidden_video.read())
                hidden_buf = BytesIO(enc_bytes)
                out = encode_video_into_video(cover_video, hidden_buf)
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