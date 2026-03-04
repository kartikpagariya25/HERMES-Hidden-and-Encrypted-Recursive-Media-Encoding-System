import io
import wave
import unittest
from PIL import Image

from core.audio.audio_to_audio import encode_audio_into_audio, decode_audio_from_audio
from core.audio.audio_to_image import encode_audio_into_image, decode_audio_from_image
from core.audio.audio_to_text import encode_audio_into_text, decode_audio_from_text
from core.audio.audio_to_video import encode_audio_into_video, decode_audio_from_video

def create_dummy_wav(content=b'\x00' * 1024):
    out = io.BytesIO()
    with wave.open(out, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(44100)
        w.writeframes(content)
    out.seek(0)
    return out

class TestAudioSteganography(unittest.TestCase):
    def setUp(self):
        # Create a tiny hidden audio file
        self.hidden_wav = create_dummy_wav(b"hidden_target_data")
        self.hidden_bytes = self.hidden_wav.read()
        self.hidden_wav.seek(0)

    def test_audio_to_audio(self):
        # Cover audio needs to be large enough
        cover_wav = create_dummy_wav(b'\x00' * 2000)
        
        stego_bytes = encode_audio_into_audio(cover_wav, self.hidden_wav)
        
        stego_io = io.BytesIO(stego_bytes)
        decoded_bytes = decode_audio_from_audio(stego_io)
        
        self.assertEqual(decoded_bytes, self.hidden_bytes)

    def test_audio_to_image(self):
        cover_img = Image.new('RGB', (100, 100), color='black')
        cover_io = io.BytesIO()
        cover_img.save(cover_io, format='PNG')
        cover_io.seek(0)
        
        stego_img = encode_audio_into_image(cover_io, self.hidden_wav)
        stego_io = io.BytesIO()
        stego_img.save(stego_io, format='PNG')
        stego_io.seek(0)
        
        decoded_bytes = decode_audio_from_image(stego_io)
        self.assertEqual(decoded_bytes, self.hidden_bytes)

    def test_audio_to_text(self):
        cover_text = "This is a cover text."
        stego_text = encode_audio_into_text(cover_text, self.hidden_wav)
        
        decoded_bytes = decode_audio_from_text(stego_text)
        self.assertEqual(decoded_bytes, self.hidden_bytes)

    def test_audio_to_video(self):
        cover_video = io.BytesIO(b"dummy_video_content")
        stego_bytes = encode_audio_into_video(cover_video, self.hidden_wav)
        
        stego_io = io.BytesIO(stego_bytes)
        decoded_bytes = decode_audio_from_video(stego_io)
        self.assertEqual(decoded_bytes, self.hidden_bytes)

if __name__ == '__main__':
    unittest.main()
