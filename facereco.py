

import os
import cv2
import face_recognition
import pandas as pd
import tempfile
import uuid
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Directory to store processed videos
PROCESSED_VIDEOS_DIR = "processed_videos"
os.makedirs(PROCESSED_VIDEOS_DIR, exist_ok=True)

# Load known faces and their names from an Excel file
def load_known_faces_from_excel(excel_file_path):
    known_face_encodings = []
    known_face_names = []

    df = pd.read_excel(excel_file_path)
    df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

    if 'ImagePath' not in df.columns or 'Name' not in df.columns:
        return known_face_encodings, known_face_names, "The Excel file must contain 'ImagePath' and 'Name' columns."

    for index, row in df.iterrows():
        image_path = row['ImagePath']
        name = row['Name']

        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(name)
    
    return known_face_encodings, known_face_names, None

# Generator to yield frames for live streaming
def generate_frames(video_path, known_face_encodings, known_face_names):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        yield b"data: Error: Could not open video.\n\n"

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break

        # Convert the frame from BGR to RGB (face_recognition uses RGB)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for any known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            name = "Unknown"

            # If a match was found in known_face_encodings, use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    video.release()

# Load known faces at the start of the API
excel_file_path = "source\Book1.xlsx"
known_face_encodings, known_face_names, error = load_known_faces_from_excel(excel_file_path)

if error:
    print(f"Error loading known faces: {error}")

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_path = temp_video_file.name
        video_file.save(temp_video_path)

    processed_video_path = os.path.join(PROCESSED_VIDEOS_DIR, str(uuid.uuid4()) + ".mp4")

    # Return the path for streaming
    return jsonify({
        "processed_video_path": processed_video_path,
        "stream_url": f"/live_stream?video_path={temp_video_path}"
    }), 200

@app.route('/live_stream')
def live_stream():
    video_path = request.args.get('video_path')
    
    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Video not found"}), 404
    
    return Response(generate_frames(video_path, known_face_encodings, known_face_names), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



