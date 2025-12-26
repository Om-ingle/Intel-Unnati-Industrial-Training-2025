import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# Install necessary libraries if not already installed

# Load the model and processor
model_id = "openai/whisper-base"  # Or any other whisper model
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)
processor = AutoProcessor.from_pretrained(model_id)

# Move the model to the GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


# Load audio file
# Replace with your actual audio file path
audio_filepath = "./samples/modi_speech.wav"

# Use librosa or other library to load audio if necessary
import librosa
audio_input, sr = librosa.load(audio_filepath, sr=16000, mono=True)

# Preprocess the audio
inputs = processor(audio_input, sampling_rate=sr, return_tensors="pt").to(device)

# Perform inference
with torch.no_grad():
  generated_ids = model.generate(**inputs)

# Decode the generated IDs to text
transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

# Print the transcribed text
print(transcription)


