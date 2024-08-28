from flask import Flask, request, jsonify, render_template
from google.cloud import storage, speech_v1p1beta1 as speech
import os

app = Flask(__name__)

# Set the path to your Google Cloud service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-key.json"

# Replace with your Google Cloud Storage bucket name
GCS_BUCKET_NAME = 'boltai_recordings'

@app.route('/')
def index():
    print("Index route was accessed")  # Debug print
    return render_template('index.html')

@app.route('/process-audio', methods=['POST'])
def process_audio():
    # Check if an audio file is included in the request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    audio_file = request.files['file']
    
    if audio_file.filename == '':
        return jsonify({'message': 'No file selected for upload'}), 400

    # Save the file locally
    file_path = os.path.join('uploads', audio_file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    audio_file.save(file_path)

    # Upload the file to Google Cloud Storage
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(audio_file.filename)
    
    try:
        blob.upload_from_filename(file_path)
        print(f"File {audio_file.filename} uploaded to {GCS_BUCKET_NAME}.")
    except Exception as e:
        print(f"Error uploading file to Google Cloud Storage: {e}")
        return jsonify({'message': 'Error uploading file to Google Cloud Storage'}), 500

    # Step 3: Transcribe audio using LongRunningRecognize
    speech_client = speech.SpeechClient()
    gcs_uri = f"gs://{GCS_BUCKET_NAME}/{audio_file.filename}"

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="ru-RU"  # Set the language to Russian
    )

    try:
        # Initiate the asynchronous transcription
        operation = speech_client.long_running_recognize(config=config, audio=audio)
        print("Waiting for operation to complete...")
        response = operation.result(timeout=3600)  # Wait up to 1 hour

    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({'message': 'Error during transcription'}), 500

    # Collect transcription results
    transcriptions = [result.alternatives[0].transcript for result in response.results]
    transcriptions_text = '\n'.join(transcriptions)

    # Save the transcriptions to a text file
    transcription_file = 'transcriptions.txt'
    try:
        with open(transcription_file, 'w') as file:
            file.write(transcriptions_text)

        # Upload the transcription file to Google Cloud Storage
        transcription_blob = bucket.blob('transcriptions.txt')
        transcription_blob.upload_from_filename(transcription_file)

        # Remove local files after processing
        os.remove(file_path)
        os.remove(transcription_file)

        return jsonify({'message': 'Transcription completed and saved to Google Cloud Storage', 'transcriptions': transcriptions}), 200
    except Exception as e:
        print(f"Error saving or uploading transcriptions: {e}")
        return jsonify({'message': 'Error saving or uploading transcriptions'}), 500

if __name__ == '__main__':
    app.run(debug=True)
