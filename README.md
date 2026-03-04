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

**HERMES** provides an elegant, easy-to-use web interface for hiding secret data within various daily media types—Text, Images, Audio, and Video files.

Using cutting-edge steganography techniques like Least Significant Bit (LSB) embedding, Zero-Width mapping, and secure EOF appending, HERMES ensures your hidden data remains entirely invisible to the naked eye (or ear!).

## ✨ Features Supported

Explore the fully implemented matrix of carrier and hidden-data pairs:

| Payload 👇 \ Carrier 👉 | **📝 Text** | **🖼️ Image** | **🎵 Audio** | **🎬 Video** | 
| :---: | :---: | :---: | :---: | :---: |
| **📝 Text**  | ✅ *Zero-Width Chars* | ✅ *LSB (PNG)* | ✅ *LSB (WAV)* | ✅ *EOF Appending* |
| **🖼️ Image** | ✅ *Zero-Width Chars* | ✅ *LSB (PNG)* | ✅ *LSB (WAV)* | ✅ *EOF Appending* |
| **🎵 Audio** | ✅ *Zero-Width Chars* | ✅ *LSB (PNG)* | ✅ *LSB (WAV)* | ✅ *EOF Appending* |

## 🚀 Getting Started

Deploy Hermes locally with just a few commands!

### Prerequisites

Ensure you have Python 3.8+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

Launch the Streamlit web server:

```bash
streamlit run app.py
```

This will automatically open the beautiful `🛰️ HERMES` application in your default web browser (typically on `http://localhost:8501`).

## 🛠️ How it Works

Hermes utilizes tailored strategies depending on the carrier medium used to disguise the payload:

- **📝 Text Carriers**: We use invisible non-printing Zero-Width characters (`\u200B`, `\u200C`) interleaved invisibly within standard text files. Reading the text file normally shows exactly what a human expects to see.
- **🖼️ Image Carriers**: Lossless **PNG** images are manipulated at the RGB Least Significant Bit (LSB) level. This microscopically alters pixel colors by a single integer value, making the change entirely visually imperceptible.
- **🎵 Audio Carriers**: Similar to images, we use LSB manipulation on uncompressed **WAV** PCM (Pulse-Code Modulation) audio frames.
- **🎬 Video Carriers**: The payload is securely appended past the standard End Of File (EOF) marker for video container streams.

## 🛡️ Security Note

Every data piece injected using Hermes includes a prepended 4-byte payload size and a 32-bit CRC32 checksum. If a file is tampered with or corrupted, Hermes will gracefully catch the discrepancy during the decoding phase.

---

## 👨‍💻 Contributors

This project was built and maintained by an amazing team of developers:

- **Kartik Pagariya** - [@KartikPagariya25](https://github.com/KartikPagariya25)
- **Aditya** - [@DevXDividends](https://github.com/DevXDividends)
- **Vikrant Kadam** - [@VikrantKadam028](https://github.com/VikrantKadam028)
- **Janhavi**
- **Pranali**

<br/>
<div align="center">
  <p><i>Keep it secret. Keep it safe. 🛰️</i></p>
</div>
