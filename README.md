<div align="center">
  <img src="https://img.icons8.com/color/120/000000/satellite-in-orbit.png" alt="Hermes Logo" width="120" />
  
  # 🛰️ HERMES
  
  **H**idden & **E**ncrypted **R**ecursive **M**edia **E**ncoding **S**ystem
  
  *A unified steganography platform to conceal anything, anywhere.*

  [![Made with Streamlit](https://img.shields.io/badge/Made_with-Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://python.org)
  [![Cryptography](https://img.shields.io/badge/Cryptography-Secure-yellow?style=for-the-badge&logo=LetsEncrypt)](https://cryptography.io)
  [![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg?style=for-the-badge)](#contributors)
  [![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/)
  [![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](#license)
  
</div>

---

## 🌟 Overview

**HERMES** provides an elegant, easy-to-use web interface for hiding secret data within various daily media types — Text, Images, Audio, and Video files.

Using cutting-edge steganography techniques like Least Significant Bit (LSB) embedding, Zero-Width character mapping, and secure EOF appending, HERMES ensures your hidden data remains entirely invisible to the naked eye (or ear!).

In addition to hiding data, HERMES now supports **end-to-end encryption** — meaning even if someone discovers the hidden data, they cannot read it without the correct password or private key.

---

## ✨ Features Supported

Explore the fully implemented matrix of carrier and hidden-data pairs:

| Payload 👇 \ Carrier 👉 | **📝 Text** | **🖼️ Image** | **🎵 Audio** | **🎬 Video** |
| :---: | :---: | :---: | :---: | :---: |
| **📝 Text**  | ✅ Zero-Width Chars | ✅ LSB (PNG) | ✅ LSB (WAV) | ✅ EOF Appending |
| **🖼️ Image** | ✅ Zero-Width Chars | ✅ LSB (PNG) | ✅ LSB (WAV) | ✅ EOF Appending |
| **🎵 Audio** | ✅ Zero-Width Chars | ✅ LSB (PNG) | ✅ LSB (WAV) | ✅ EOF Appending |
| **🎬 Video** | ✅ EOF Appending | ✅ EOF Appending | ✅ EOF Appending | ✅ EOF Appending |

> **Note:** All 16 combinations are now fully supported. Video payloads use fast EOF Appending across all carriers — no size limits!

---

## 🔐 Encryption (New Feature)

HERMES now supports **two encryption modes** to protect your hidden data. Even if someone extracts the hidden bytes, they cannot read them without the correct key.

### Mode 1 — Password (AES-256-GCM + PBKDF2)

Both the sender and receiver agree on a shared password beforehand (e.g., via WhatsApp or in person). HERMES uses this password to encrypt the data before hiding it.

- **PBKDF2** converts your password into a strong 256-bit encryption key
- **AES-256-GCM** encrypts the data — the same standard used by banks and governments
- A random **salt** is generated every time, so the same password produces different encryption each time
- The **GCM tag** automatically detects if anyone tampers with the file

### Mode 2 — Keypair (RSA-OAEP + AES-256-GCM)

No shared password needed. The receiver generates a keypair — a **public key** and a **private key**. The receiver shares only the public key with the sender.

- Sender encrypts using the receiver's **public key** (like a padlock anyone can close)
- Only the receiver's **private key** can decrypt it (like the unique key that opens that padlock)
- Even if the sender's device is compromised, the data stays safe — the private key never leaves the receiver's device

**How to use Keypair mode:**

1. **Receiver** opens HERMES → Encryption → Keypair → click **"Generate keypair"**
2. Download **both** files immediately — `hermes_private.pem` and `hermes_public.pem`
3. **Receiver** sends `hermes_public.pem` to the sender (email, WhatsApp — it's safe to share)
4. **Sender** selects Keypair mode → uploads `hermes_public.pem` → encodes the message
5. **Receiver** selects Keypair mode → uploads `hermes_private.pem` → decodes the message

> ⚠️ **Never share your private key.** If someone gets your private key, they can decrypt all your messages.

---

## 📁 Project Structure

```
HERMES/
├── app.py                  ← Main Streamlit application
├── crypto.py               ← Encryption & decryption module
├── requirements.txt
└── core/
    ├── text/
    │   ├── text_to_text.py
    │   ├── text_to_image.py
    │   ├── text_to_audio.py
    │   └── text_to_video.py
    ├── image/
    │   ├── image_to_text.py
    │   ├── image_to_image.py
    │   ├── image_to_audio.py
    │   └── image_to_video.py
    ├── audio/
    │   ├── audio_to_text.py
    │   ├── audio_to_image.py
    │   ├── audio_to_audio.py
    │   └── audio_to_video.py
    └── video/
        ├── video_to_text.py
        ├── video_to_image.py
        ├── video_to_audio.py
        └── video_to_video.py
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have **Python 3.8+** installed.

**Install FFmpeg** (required for Video steganography):

| OS | Command |
|---|---|
| Windows | `winget install ffmpeg` |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` |

Verify installation:
```bash
ffmpeg -version
```

**Install Python dependencies:**
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

This will open HERMES in your browser at `http://localhost:8501`.

---

## 🛠️ How it Works

HERMES uses different techniques depending on the carrier type:

- **📝 Text Carriers** — Invisible zero-width Unicode characters (`\u200B`, `\u200C`) are inserted between the visible text. The cover text looks completely normal when read.
- **🖼️ Image Carriers** — Lossless PNG images are modified at the Least Significant Bit (LSB) of each pixel's RGB channels. A 1-bit change per channel is completely invisible to the human eye.
- **🎵 Audio Carriers** — The same LSB technique is applied to the raw PCM frames of WAV audio files. The audio sounds identical before and after.
- **🎬 Video Carriers** — Hidden data is appended after the video's End-Of-File (EOF) marker. The video plays perfectly — media players simply ignore anything after the EOF. This method is fast and has no size limit.

---

## 🛡️ Security Details

Every hidden payload includes:
- **4-byte length header** — to know exactly how many bytes to extract
- **32-bit CRC32 checksum** — to detect any corruption or tampering

When encryption is enabled, the full encrypted blob (salt + nonce + ciphertext + GCM tag) is what gets embedded — so even raw extraction reveals nothing readable.

---

## 🧪 Testing Guide

### Test 1 — Basic Steganography (No Encryption)

> Goal: Confirm hiding and extracting works correctly.

1. Open HERMES → Sidebar → `Encryption = None`
2. Set `Data to hide = Text`, `Carrier = Image`, `Operation = Encode`
3. Upload any PNG image as cover
4. Type `Hello HERMES` in the hidden text box → click **Encode** → download the image
5. Switch to `Operation = Decode` → upload the downloaded image → click **Decode**
6. ✅ You should see `Hello HERMES`

---

### Test 2 — Password Encryption (Happy Path)

> Goal: Confirm encryption and decryption work with the correct password.

1. Sidebar → `Encryption = Password (AES-GCM)`
2. `Operation = Encode` → enter password `test123` → encode a message → download file
3. Switch to `Operation = Decode` → enter same password `test123` → decode
4. ✅ Original message should appear

---

### Test 3 — Wrong Password Attack (Security Test)

> Goal: Confirm a third party with the wrong password cannot read the message.

1. Use the same encoded file from Test 2
2. `Operation = Decode` → enter wrong password `wrongpass` → click Decode
3. ✅ You should see a **red error**: `Decryption failed — wrong password or corrupted data`

This confirms HERMES is secure — the file is useless without the correct password.

---

### Test 4 — Keypair Encryption (Happy Path)

> Goal: Confirm RSA keypair encryption works end-to-end.

1. Sidebar → `Encryption = Keypair (RSA + AES-GCM)`
2. Click **"Generate keypair"** → download **both** `hermes_private.pem` and `hermes_public.pem` immediately
3. `Operation = Encode` → upload `hermes_public.pem` → hide a message → download stego file
4. `Operation = Decode` → upload `hermes_private.pem` → decode
5. ✅ Original message should appear

---

### Test 5 — Wrong Private Key Attack (Security Test)

> Goal: Confirm a different private key cannot decrypt the message.

1. Click **"Generate keypair"** again → download the **new** `hermes_private.pem`
2. Try to decode the file from Test 4 using this **new** private key
3. ✅ You should see a **red error**: `Decryption failed — wrong private key or corrupted data`

This confirms that only the matching private key can decrypt the message.

---

### Test 6 — Video Encoding (Fast EOF)

> Goal: Confirm Video carrier works without size limits.

1. Sidebar → `Data to hide = Video`, `Carrier = Video`, `Encryption = None`
2. Upload any two MP4 files (cover and hidden)
3. Click **Encode** → should complete in seconds ✅
4. Switch to Decode → upload the stego video → click Decode
5. ✅ Hidden video should be extracted and available for download

---

### Quick Test Reference

| Test | Expected Result |
|---|---|
| No encryption encode/decode | Original data returned |
| Correct password | Original data returned |
| Wrong password | Red error shown |
| Correct private key | Original data returned |
| Wrong private key | Red error shown |
| Video → Video | Encodes in seconds, no size limit |

---

## 👨‍💻 Contributors

This project was built and maintained by an amazing team of developers:

- **Kartik Pagariya** — [@KartikPagariya25](https://github.com/KartikPagariya25)
- **Aditya** — [@DevXDividends](https://github.com/DevXDividends)
- **Vikrant Kadam** — [@VikrantKadam028](https://github.com/VikrantKadam028)
- **Janhavi**
- **Pranali**

---

<div align="center">
  <p><i>Keep it secret. Keep it safe. 🛰️</i></p>
</div>