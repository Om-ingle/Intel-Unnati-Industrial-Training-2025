import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import librosa

# Load the model and processor
model_id = "facebook/wav2vec2-base-960h"  # Replace with your desired Wav2Vec 2.0 model
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# Load audio file
audio_filepath = "./samples/modi_speech.wav"
audio_input, sr = librosa.load(audio_filepath, sr=16000, mono=True) # Ensure consistent sample rate

# Preprocess the audio
inputs = processor(audio_input, sampling_rate=sr, return_tensors="pt").input_values  

# Perform inference
with torch.no_grad():
     logits = model(inputs).logits

# Decode the generated IDs to text
 # take argmax and decode
predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)

print(transcription)
