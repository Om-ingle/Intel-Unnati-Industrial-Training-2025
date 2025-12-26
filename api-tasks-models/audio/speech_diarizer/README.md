# Speech diarizer 


## Setup
1. Create the virtual env: `uv venv`
2. Activate the virtual env: `source .venv/bin/activate`
3. Install the requirements: `uv pip install -r requirements.txt`
4. Add your huggingface token in the script
5. Run the script: `python main.py`


## How to access the model
1. visit hf.co/pyannote/speaker-diarization and accept user conditions
2. visit hf.co/pyannote/segmentation and accept user conditions
3. visit hf.co/settings/tokens to create an access token
4. instantiate pretrained speaker diarization pipeline