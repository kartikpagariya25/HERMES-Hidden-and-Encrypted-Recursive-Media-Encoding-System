from PIL import Image
import numpy as np

# Random pixels se bani image — bilkul valid PNG
img = Image.fromarray(np.random.randint(0, 255, (2000, 2000, 3), dtype=np.uint8))
img.save("cover_image.png")
import numpy as np
import wave, struct

samples = np.random.randint(-32768, 32767, 500000, dtype=np.int16)

with wave.open("cover_audio.wav", "w") as f:
    f.setnchannels(1)        # Mono
    f.setsampwidth(2)        # 16-bit
    f.setframerate(44100)    # CD quality
    f.writeframes(samples.tobytes())

print("Done! cover_audio.wav ready hai")