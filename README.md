## Transcribing Web App

A minimal Flask application for uploading audio files, transcribing them with Google Cloud Speech-to-Text (LongRunningRecognize), and storing both the audio and transcription in a Google Cloud Storage bucket.

---

### Features

- Upload audio files via a web form
- Store uploaded audio in a Google Cloud Storage bucket
- Perform asynchronous transcription of audio (MP3) in Russian (`ru-RU`)
- Save transcription results to a text file
- Upload the transcription file back to the same GCS bucket
- Automatic cleanup of local files after processing

---

### Prerequisites

- Python 3.7 or higher
- A Google Cloud project with the Speech-to-Text and Cloud Storage APIs enabled
- A service account JSON key with permissions to read/write to your GCS bucket
- The following Python packages:
  - Flask
  - google-cloud-storage
  - google-cloud-speech

---

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install Flask google-cloud-storage google-cloud-speech
   ```

---

### Configuration

1. **Service Account Key**
   - Download your service account JSON key from Google Cloud Console.
   - Save it as `google-key.json` in the project root (or another secure location).

2. **Environment Variable**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google-key.json"
   ```

3. **Bucket Name**
   - In `app.py`, update the constant `GCS_BUCKET_NAME` with your bucket:
     ```python
     GCS_BUCKET_NAME = 'your-bucket-name'
     ```

---

### Usage

1. **Run the Flask app**

   ```bash
   python app.py
   ```

2. **Open** `http://localhost:5000/` in your browser.
3. **Upload** an MP3 audio file in the form.
4. **Wait** for the transcription to complete.  
   - The server will print debug messages:
     ```text
     File yourfile.mp3 uploaded to boltai_recordings.
     Waiting for operation to complete...
     Transcription completed and saved to Google Cloud Storage.
     ```
5. **Retrieve**:
   - `yourfile.mp3` and `transcriptions.txt` will be in your GCS bucket.

---

### Project Structure

```
├── app.py               # Flask application
├── google-key.json      # GCP credentials (ignored by Git)
├── templates/
│   └── index.html       # Upload form
├── uploads/             # Temporary storage for uploads
├── transcriptions.txt   # Generated transcript (temp)
└── requirements.txt     # Dependency list
```

---

### API Endpoint

- **POST** `/process-audio`
  - Form field: `file` (audio file upload)
  - **Success Response** (HTTP 200):
    ```json
    {
      "message": "Transcription completed and saved to Google Cloud Storage",
      "transcriptions": [
        "First line of transcript...",
        "Second line of transcript...",
        "..."
      ]
    }
    ```
  - **Error Responses**:
    - 400: Missing file or no file selected
    - 500: Error uploading to GCS or during transcription

---

### Notes

- Ensure that the service account has both **Storage Object Admin** and **Speech API User** roles.
- The `long_running_recognize` method may take several minutes for larger files.
- Files are removed from local storage after successful upload to avoid buildup.

---

### License

This project is licensed under the MIT License. Feel free to adapt and extend as needed.

