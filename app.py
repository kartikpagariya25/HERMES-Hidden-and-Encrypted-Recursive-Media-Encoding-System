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




st.set_page_config(page_title="🛰️ HERMES", page_icon="🛰️", layout="centered")

st.title("🛰️ HERMES")
st.caption("Hidden & Encrypted Recursive Media Encoding System")

st.sidebar.header("⚙️ Configuration")
hidden_type = st.sidebar.selectbox("Data to hide", ["Text", "Image", "Audio", "Video"])
carrier_type = st.sidebar.selectbox("Carrier type", ["Text", "Image", "Audio", "Video"])
operation = st.sidebar.radio("Operation", ["Encode", "Decode"])

implemented_pairs = {
    ("Text", "Text"),
    ("Text", "Image"),
    ("Text", "Audio"),
    ("Text", "Video"),
    ("Image", "Image"),
    ("Image", "Video"),
    ("Image", "Text"),
    ("Image", "Audio"),
    ("Audio", "Audio")
}


if (hidden_type, carrier_type) not in implemented_pairs:
    st.stop()

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


