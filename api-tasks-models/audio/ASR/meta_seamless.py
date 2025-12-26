import torch
import torchaudio
from transformers import SeamlessM4TModel, AutoProcessor
import librosa

# Load the model and processor
model_id = "facebook/hf-seamless-m4t-large"  # Or another SeamlessM4T model
model = SeamlessM4TModel.from_pretrained(model_id).to("cuda" if torch.cuda.is_available() else "cpu")
processor = AutoProcessor.from_pretrained(model_id)

# Load audio file
# Read an audio file and resample to 16kHz:
audio, orig_freq =  torchaudio.load("./samples/sample.wav")
audio =  torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000) # must be a 16 kHz waveform array
audio_inputs = processor(audios=audio, return_tensors="pt")

output_tokens = model.generate(**audio_inputs, tgt_lang="fra", generate_speech=False)
transcription = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

print(transcription)
