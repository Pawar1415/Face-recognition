# import os
# import cv2
# import face_recognition
# import pandas as pd
# import tempfile
# import uuid
# from flask import Flask, request, jsonify, Response, send_file

# app = Flask(__name__)

# # Directory to store processed videos
# PROCESSED_VIDEOS_DIR = "processed_videos"
# os.makedirs(PROCESSED_VIDEOS_DIR, exist_ok=True)

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         return known_face_encodings, known_face_names, "The Excel file must contain 'ImagePath' and 'Name' columns."

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
    
#     return known_face_encodings, known_face_names, None

# # Generator to yield frames for live streaming and save processed video
# def generate_frames(video_path, processed_video_path, known_face_encodings, known_face_names):
#     video = cv2.VideoCapture(video_path)
#     if not video.isOpened():
#         yield b"data: Error: Could not open video.\n\n"

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(processed_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     while video.isOpened():
#         success, frame = video.read()
#         if not success:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#         # Write the frame to the output video
#         out.write(frame)

#     video.release()
#     out.release()

# # Load known faces at the start of the API
# excel_file_path = "Book1.xlsx"
# known_face_encodings, known_face_names, error = load_known_faces_from_excel(excel_file_path)

# if error:
#     print(f"Error loading known faces: {error}")

# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400

#     video_file = request.files['video']

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#         video_file.save(temp_video_path)

#     processed_video_path = os.path.join(PROCESSED_VIDEOS_DIR, str(uuid.uuid4()) + ".mp4")

#     # Return the path for streaming and downloading
#     return jsonify({
#         "processed_video_path": processed_video_path,
#         "stream_url": f"/live_stream?video_path={temp_video_path}&processed_video_path={processed_video_path}"
#     }), 200

# @app.route('/live_stream')
# def live_stream():
#     video_path = request.args.get('video_path')
#     processed_video_path = request.args.get('processed_video_path')
    
#     if not video_path or not os.path.exists(video_path):
#         return jsonify({"error": "Video not found"}), 404
    
#     return Response(generate_frames(video_path, processed_video_path, known_face_encodings, known_face_names), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/download_processed_video', methods=['GET'])
# def download_processed_video():
#     processed_video_path = request.args.get('path')
    
#     if not processed_video_path or not os.path.exists(processed_video_path):
#         return jsonify({"error": "Processed video not found"}), 404

#     return send_file(processed_video_path, as_attachment=True, download_name='processed_video.mp4')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)




















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
excel_file_path = "Book1.xlsx"
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
















# import os
# import cv2
# import face_recognition
# import pandas as pd
# import tempfile
# import uuid
# from flask import Flask, request, jsonify, Response

# app = Flask(__name__)

# # Directory to store processed videos
# PROCESSED_VIDEOS_DIR = "processed_videos"
# os.makedirs(PROCESSED_VIDEOS_DIR, exist_ok=True)

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         return known_face_encodings, known_face_names, "The Excel file must contain 'ImagePath' and 'Name' columns."

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
    
#     return known_face_encodings, known_face_names, None

# # Generator to yield frames for live streaming
# def generate_frames(video_path, known_face_encodings, known_face_names):
#     video = cv2.VideoCapture(video_path)
#     if not video.isOpened():
#         yield None, "Error: Could not open video."

#     while video.isOpened():
#         success, frame = video.read()
#         if not success:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
        
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#     video.release()

# # Load known faces at the start of the API
# excel_file_path = "Book1.xlsx"
# known_face_encodings, known_face_names, error = load_known_faces_from_excel(excel_file_path)

# if error:
#     print(f"Error loading known faces: {error}")

# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400

#     video_file = request.files['video']

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#         video_file.save(temp_video_path)

#     processed_video_path = os.path.join(PROCESSED_VIDEOS_DIR, str(uuid.uuid4()) + ".mp4")
    
#     def generate():
#         for frame in generate_frames(temp_video_path, known_face_encodings, known_face_names):
#             if frame is None:
#                 yield 'data: %s\n\n' % "Error: Could not open video."
#             else:
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
#     return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/get_processed_video', methods=['GET'])
# def get_processed_video():
#     processed_video_path = request.args.get('path')
    
#     if not processed_video_path or not os.path.exists(processed_video_path):
#         return jsonify({"error": "Processed video not found"}), 404

#     return send_file(processed_video_path, as_attachment=True, download_name='processed_video.mp4')

# @app.route('/live_stream')
# def live_stream():
#     video_path = request.args.get('video_path')
    
#     if not video_path or not os.path.exists(video_path):
#         return jsonify({"error": "Video not found"}), 404
    
#     return Response(generate_frames(video_path, known_face_encodings, known_face_names), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)















# import os
# import cv2
# import face_recognition
# import pandas as pd
# import tempfile
# import uuid
# from flask import Flask, request, jsonify, send_file, Response

# app = Flask(__name__)

# # Directory to store processed videos
# PROCESSED_VIDEOS_DIR = "processed_videos"
# os.makedirs(PROCESSED_VIDEOS_DIR, exist_ok=True)

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         return known_face_encodings, known_face_names, "The Excel file must contain 'ImagePath' and 'Name' columns."

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
    
#     return known_face_encodings, known_face_names, None

# # Function to detect faces in video frames and recognize them
# def video_face_detection(video_path, known_face_encodings, known_face_names):
#     # Create a unique file name for the output video
#     unique_filename = str(uuid.uuid4()) + ".mp4"
#     output_video_path = os.path.join(PROCESSED_VIDEOS_DIR, unique_filename)

#     # Capture video from the given file path
#     video = cv2.VideoCapture(video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         return None, "Error: Could not open video."

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     return output_video_path, None

# # Load known faces at the start of the API
# excel_file_path = "Book1.xlsx"
# known_face_encodings, known_face_names, error = load_known_faces_from_excel(excel_file_path)

# if error:
#     print(f"Error loading known faces: {error}")

# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400

#     video_file = request.files['video']

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#         video_file.save(temp_video_path)

#     processed_video_path, error = video_face_detection(temp_video_path, known_face_encodings, known_face_names)

#     if error:
#         return jsonify({"error": error}), 500

#     return jsonify({"processed_video_path": processed_video_path, "stream_url": "/live_stream"}), 200

# @app.route('/get_processed_video', methods=['GET'])
# def get_processed_video():
#     processed_video_path = request.args.get('path')
    
#     if not processed_video_path or not os.path.exists(processed_video_path):
#         return jsonify({"error": "Processed video not found"}), 404

#     return send_file(processed_video_path, as_attachment=True, download_name='processed_video.mp4')

# @app.route('/live_stream')
# def live_stream():
#     video_path = request.args.get('video_path')
    
#     if not video_path or not os.path.exists(video_path):
#         return jsonify({"error": "Video not found"}), 404
    
#     def generate_frames(video_path):
#         video = cv2.VideoCapture(video_path)
        
#         while True:
#             success, frame = video.read()
#             if not success:
#                 break
            
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
            
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
#     return Response(generate_frames(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)








# import os
# import cv2
# import face_recognition
# import pandas as pd
# import tempfile
# import uuid
# from flask import Flask, request, jsonify, send_file

# app = Flask(__name__)

# # Directory to store processed videos
# PROCESSED_VIDEOS_DIR = "processed_videos"
# os.makedirs(PROCESSED_VIDEOS_DIR, exist_ok=True)

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         return known_face_encodings, known_face_names, "The Excel file must contain 'ImagePath' and 'Name' columns."

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
    
#     return known_face_encodings, known_face_names, None

# # Function to detect faces in video frames and recognize them
# def video_face_detection(video_path, known_face_encodings, known_face_names):
#     # Create a unique file name for the output video
#     unique_filename = str(uuid.uuid4()) + ".mp4"
#     output_video_path = os.path.join(PROCESSED_VIDEOS_DIR, unique_filename)

#     # Capture video from the given file path
#     video = cv2.VideoCapture(video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         return None, "Error: Could not open video."

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     return output_video_path, None

# # Load known faces at the start of the API
# excel_file_path = "Book1.xlsx"
# known_face_encodings, known_face_names, error = load_known_faces_from_excel(excel_file_path)

# if error:
#     print(f"Error loading known faces: {error}")

# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400

#     video_file = request.files['video']

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#         video_file.save(temp_video_path)

#     processed_video_path, error = video_face_detection(temp_video_path, known_face_encodings, known_face_names)

#     if error:
#         return jsonify({"error": error}), 500

#     return jsonify({"processed_video_path": processed_video_path}), 200

# @app.route('/get_processed_video', methods=['GET'])
# def get_processed_video():
#     processed_video_path = request.args.get('path')
    
#     if not processed_video_path or not os.path.exists(processed_video_path):
#         return jsonify({"error": "Processed video not found"}), 404

#     return send_file(processed_video_path, as_attachment=True, download_name='processed_video.mp4')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

















# import os
# import cv2
# import face_recognition
# import pandas as pd
# import tempfile
# from flask import Flask, request, jsonify, send_file

# app = Flask(__name__)

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         return known_face_encodings, known_face_names, "The Excel file must contain 'ImagePath' and 'Name' columns."

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
    
#     return known_face_encodings, known_face_names, None

# # Function to detect faces in video frames and recognize them
# def video_face_detection(video_path, known_face_encodings, known_face_names):
#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     # Capture video from the given file path
#     video = cv2.VideoCapture(video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         return None, "Error: Could not open video."

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     return output_video_path, None

# # Load known faces at the start of the API
# excel_file_path = "Book1.xlsx"
# known_face_encodings, known_face_names, error = load_known_faces_from_excel(excel_file_path)

# if error:
#     print(f"Error loading known faces: {error}")

# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400

#     video_file = request.files['video']

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#         video_file.save(temp_video_path)

#     processed_video_path, error = video_face_detection(temp_video_path, known_face_encodings, known_face_names)

#     if error:
#         return jsonify({"error": error}), 500

#     return send_file(processed_video_path, as_attachment=True, download_name='processed_video.mp4')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
















# import os
# import cv2
# import face_recognition
# import pandas as pd
# import tempfile
# from flask import Flask, request, jsonify, send_file

# app = Flask(__name__)

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         return known_face_encodings, known_face_names, "The Excel file must contain 'ImagePath' and 'Name' columns."

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
    
#     return known_face_encodings, known_face_names, None

# # Function to detect faces in video frames and recognize them
# def video_face_detection(video_path, known_face_encodings, known_face_names):
#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     # Capture video from the given file path
#     video = cv2.VideoCapture(video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         return None, "Error: Could not open video."

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     return output_video_path, None

# # Load known faces at the start of the API
# excel_file_path = "Book1.xlsx"
# known_face_encodings, known_face_names, error = load_known_faces_from_excel(excel_file_path)

# if error:
#     print(f"Error loading known faces: {error}")

# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400

#     video_file = request.files['video']

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#         video_file.save(temp_video_path)

#     processed_video_path, error = video_face_detection(temp_video_path, known_face_encodings, known_face_names)

#     if error:
#         return jsonify({"error": error}), 500

#     return send_file(processed_video_path, as_attachment=True, attachment_filename='processed_video.mp4')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)










# import os
# import cv2
# import face_recognition
# import pandas as pd
# import tempfile
# from flask import Flask, request, jsonify, send_file

# app = Flask(__name__)

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         return known_face_encodings, known_face_names, "The Excel file must contain 'ImagePath' and 'Name' columns."

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
    
#     return known_face_encodings, known_face_names, None

# # Function to detect faces in video frames and recognize them
# def video_face_detection(video_path, known_face_encodings, known_face_names):
#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     # Capture video from the given file path
#     video = cv2.VideoCapture(video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         return None, "Error: Could not open video."

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     return output_video_path, None

# # Load known faces at the start of the API
# excel_file_path = "Book1.xlsx"
# known_face_encodings, known_face_names, error = load_known_faces_from_excel(excel_file_path)

# if error:
#     print(f"Error loading known faces: {error}")

# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400

#     video_file = request.files['video']

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#         video_file.save(temp_video_path)

#     processed_video_path, error = video_face_detection(temp_video_path, known_face_encodings, known_face_names)

#     if error:
#         return jsonify({"error": error}), 500

#     return send_file(processed_video_path, as_attachment=True, attachment_filename='processed_video.mp4')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
















# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd
# import os
# import tempfile

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     # Write the uploaded video to a temporary file
#     with open(temp_video_path, "wb") as f:
#         f.write(uploaded_file.read())

#     # Capture video from the temporary file
#     video = cv2.VideoCapture(temp_video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         st.error("Error: Could not open video.")
#         return None

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     # Remove the temporary input file
#     os.remove(temp_video_path)

#     return output_video_path

# # Streamlit app
# def run_streamlit_app():
#     st.title("Video Face Recognition App")
#     st.write("Upload a video file and the app will recognize faces.")

#     # Path to the Excel file
#     excel_file_path = "Book1.xlsx"

#     # Load known faces
#     known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

#     # GUI file uploader for video file
#     uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

#     # Start face recognition when a video file is uploaded
#     if uploaded_file is not None:
#         processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
        
#         # Display the processed video and add download button
#         if processed_video_path:
#             st.video(processed_video_path)
            
#             # Provide a download link for the processed video
#             with open(processed_video_path, "rb") as video_file:
#                 video_bytes = video_file.read()
#                 st.download_button(
#                     label="Download Processed Video",
#                     data=video_bytes,
#                     file_name="processed_video.mp4",
#                     mime="video/mp4"
#                 )

# if __name__ == "__main__":
#     run_streamlit_app()





# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd
# import os
# import tempfile
# from flask import Flask, request, jsonify

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     # Write the uploaded video to a temporary file
#     with open(temp_video_path, "wb") as f:
#         f.write(uploaded_file.read())

#     # Capture video from the temporary file
#     video = cv2.VideoCapture(temp_video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         st.error("Error: Could not open video.")
#         return None

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     # Remove the temporary input file
#     os.remove(temp_video_path)

#     return output_video_path

# # Streamlit app
# def run_streamlit_app():
#     st.title("Video Face Recognition App")
#     st.write("Upload a video file and the app will recognize faces.")

#     # Path to the Excel file
#     excel_file_path = "Book1.xlsx"

#     # Load known faces
#     known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

#     # GUI file uploader for video file
#     uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

#     # Start face recognition when a video file is uploaded
#     if uploaded_file is not None:
#         processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
        
#         # Display the processed video and add download button
#         if processed_video_path:
#             st.video(processed_video_path)
            
#             # Provide a download link for the processed video
#             with open(processed_video_path, "rb") as video_file:
#                 video_bytes = video_file.read()
#                 st.download_button(
#                     label="Download Processed Video",
#                     data=video_bytes,
#                     file_name="processed_video.mp4",
#                     mime="video/mp4"
#                 )

# # Flask API for face recognition
# app = Flask(__name__)

# @app.route('/api/recognize_faces', methods=['POST'])
# def recognize_faces():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     excel_file_path = "Book1.xlsx"
#     known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#         file.save(temp_video_path)

#     video = cv2.VideoCapture(temp_video_path)
#     if not video.isOpened():
#         return jsonify({"error": "Could not open video"}), 400

#     temp_output_path = tempfile.mktemp(suffix=".mp4")
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(temp_output_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         rgb_frame = frame[:, :, ::-1]
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         out.write(frame)

#     video.release()
#     out.release()

#     return jsonify({"message": "Faces recognized", "video_path": temp_output_path})

# if __name__ == "__main__":
#     mode = st.radio("Choose Mode", ["Streamlit App", "API"])
#     if mode == "Streamlit App":
#         run_streamlit_app()
#     elif mode == "API":
#         app.run(debug=True, host='0.0.0.0', port=5000)














# from fastapi import FastAPI, UploadFile, File, HTTPException
# import face_recognition
# import pandas as pd
# import cv2
# import os
# import tempfile

# app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Video Face Recognition API. Use /upload-video/ to upload a video."}

# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         raise ValueError("The Excel file must contain 'ImagePath' and 'Name' columns.")

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         try:
#             image = face_recognition.load_image_file(image_path)
#             encodings = face_recognition.face_encodings(image)
#             if encodings:
#                 known_face_encodings.append(encodings[0])
#                 known_face_names.append(name)
#             else:
#                 print(f"No faces found in image {image_path}")
#         except Exception as e:
#             print(f"Error loading image {image_path}: {e}")

#     return known_face_encodings, known_face_names

# def video_face_detection(uploaded_file_path, known_face_encodings, known_face_names):
#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     try:
#         # Capture video from the uploaded file path
#         video = cv2.VideoCapture(uploaded_file_path)

#         # Check if video opened successfully
#         if not video.isOpened():
#             raise ValueError("Error: Could not open video.")

#         # Create a VideoWriter object to save the processed video
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#         # Continuously process video feed and display in window until the end of the video
#         while video.isOpened():
#             check, frame = video.read()
#             if not check:
#                 break

#             # Convert the frame from BGR to RGB (face_recognition uses RGB)
#             rgb_frame = frame[:, :, ::-1]

#             # Find all the faces and face encodings in the current frame of video
#             face_locations = face_recognition.face_locations(rgb_frame)
#             face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#             # Loop through each face in this frame of video
#             for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                 # See if the face is a match for any known face(s)
#                 matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#                 name = "Unknown"

#                 # If a match was found in known_face_encodings, use the first one.
#                 if True in matches:
#                     first_match_index = matches.index(True)
#                     name = known_face_names[first_match_index]

#                 # Draw a box around the face
#                 cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#                 # Draw a label with a name below the face
#                 cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#                 font = cv2.FONT_HERSHEY_DUPLEX
#                 cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#             # Write the frame with recognized faces to the output video
#             out.write(frame)

#         # Release the video capture and writer
#         video.release()
#         out.release()

#     except Exception as e:
#         print(f"Error processing video: {e}")
#         return None

#     return output_video_path

# @app.post("/upload-video/")
# async def upload_video(file: UploadFile = File(...), excel_file_path: str = "Book1.xlsx"):
#     try:
#         # Load known faces
#         known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

#         # Save uploaded file to a temporary location
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
#             temp_file.write(file.file.read())
#             temp_file_path = temp_file.name

#         # Process the video for face recognition
#         processed_video_path = video_face_detection(temp_file_path, known_face_encodings, known_face_names)

#         # Clean up the temporary input file
#         if os.path.exists(temp_file_path):
#             os.remove(temp_file_path)

#         if processed_video_path:
#             return {"processed_video_path": processed_video_path}
#         else:
#             raise HTTPException(status_code=500, detail="Error processing video.")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)











# from fastapi import FastAPI, UploadFile, File, HTTPException
# import face_recognition
# import pandas as pd
# import cv2
# import os
# import tempfile

# app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Video Face Recognition API. Use /upload-video/ to upload a video."}

# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         raise ValueError("The Excel file must contain 'ImagePath' and 'Name' columns.")

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         try:
#             image = face_recognition.load_image_file(image_path)
#             encodings = face_recognition.face_encodings(image)
#             if encodings:
#                 known_face_encodings.append(encodings[0])
#                 known_face_names.append(name)
#             else:
#                 print(f"No faces found in image {image_path}")
#         except Exception as e:
#             print(f"Error loading image {image_path}: {e}")

#     return known_face_encodings, known_face_names

# def video_face_detection(uploaded_file_path, known_face_encodings, known_face_names):
#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     try:
#         # Capture video from the uploaded file path
#         video = cv2.VideoCapture(uploaded_file_path)

#         # Check if video opened successfully
#         if not video.isOpened():
#             raise ValueError("Error: Could not open video.")

#         # Create a VideoWriter object to save the processed video
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#         # Continuously process video feed and display in window until the end of the video
#         while video.isOpened():
#             check, frame = video.read()
#             if not check:
#                 break

#             # Convert the frame from BGR to RGB (face_recognition uses RGB)
#             rgb_frame = frame[:, :, ::-1]

#             # Find all the faces and face encodings in the current frame of video
#             face_locations = face_recognition.face_locations(rgb_frame)
#             face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#             # Loop through each face in this frame of video
#             for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                 # See if the face is a match for any known face(s)
#                 matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#                 name = "Unknown"

#                 # If a match was found in known_face_encodings, use the first one.
#                 if True in matches:
#                     first_match_index = matches.index(True)
#                     name = known_face_names[first_match_index]

#                 # Draw a box around the face
#                 cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#                 # Draw a label with a name below the face
#                 cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#                 font = cv2.FONT_HERSHEY_DUPLEX
#                 cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#             # Write the frame with recognized faces to the output video
#             out.write(frame)

#         # Release the video capture and writer
#         video.release()
#         out.release()

#     except Exception as e:
#         print(f"Error processing video: {e}")
#         return None

#     return output_video_path

# @app.post("/upload-video/")
# async def upload_video(file: UploadFile = File(...), excel_file_path: str = "Book1.xlsx"):
#     try:
#         # Load known faces
#         known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

#         # Save uploaded file to a temporary location
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
#             temp_file.write(file.file.read())
#             temp_file_path = temp_file.name

#         # Process the video for face recognition
#         processed_video_path = video_face_detection(temp_file_path, known_face_encodings, known_face_names)

#         # Clean up the temporary input file
#         if os.path.exists(temp_file_path):
#             os.remove(temp_file_path)

#         if processed_video_path:
#             return {"processed_video_path": processed_video_path}
#         else:
#             raise HTTPException(status_code=500, detail="Error processing video.")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)












# import streamlit as st
# import requests
# import os

# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # Path to the Excel file
# excel_file_path = "Book1.xlsx"

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     # Save uploaded file to a temporary location
#     with open("temp_video.mp4", "wb") as f:
#         f.write(uploaded_file.read())

#     with st.spinner('Processing...'):
#         # Send video to API for processing
#         with open("temp_video.mp4", "rb") as f:
#             response = requests.post(
#                 "http://localhost:8000/upload-video/",
#                 files={"file": f},
#                 data={"excel_file_path": excel_file_path}
#             )

#         if response.status_code == 200:
#             processed_video_path = response.json().get("processed_video_path")

#             # Display the processed video and add download button
#             if processed_video_path:
#                 st.video(processed_video_path)
                
#                 # Provide a download link for the processed video
#                 with open(processed_video_path, "rb") as video_file:
#                     video_bytes = video_file.read()
#                     st.download_button(
#                         label="Download Processed Video",
#                         data=video_bytes,
#                         file_name="processed_video.mp4",
#                         mime="video/mp4"
#                     )
                
#                 # Clean up the temporary processed video file
#                 os.remove(processed_video_path)
#         else:
#             st.error("Error processing video.")
        
#     # Clean up the temporary uploaded video file
#     os.remove("temp_video.mp4")












# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd
# import os
# import tempfile

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     # Write the uploaded video to a temporary file
#     with open(temp_video_path, "wb") as f:
#         f.write(uploaded_file.read())

#     # Capture video from the temporary file
#     video = cv2.VideoCapture(temp_video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         st.error("Error: Could not open video.")
#         return None

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     # Remove the temporary input file
#     os.remove(temp_video_path)

#     return output_video_path

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # Path to the Excel file
# excel_file_path = "Book1.xlsx"

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video and add download button
#     if processed_video_path:
#         st.video(processed_video_path)
        
#         # Provide a download link for the processed video
#         with open(processed_video_path, "rb") as video_file:
#             video_bytes = video_file.read()
#             st.download_button(
#                 label="Download Processed Video",
#                 data=video_bytes,
#                 file_name="processed_video.mp4",
#                 mime="video/mp4"
#             )













# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd
# import os

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     temp_video_path = "temp_video.mp4"
#     with open(temp_video_path, "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture(temp_video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         st.error("Error: Could not open video.")
#         return None

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     output_path = "processed_video.mp4"
#     out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     # Remove the temporary file
#     os.remove(temp_video_path)

#     return output_path

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # Path to the Excel file
# excel_file_path = "Book1.xlsx"

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     if processed_video_path:
#         st.video(processed_video_path)










# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd
# import os

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     temp_video_path = "temp_video.mp4"
#     with open(temp_video_path, "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture(temp_video_path)

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     # Remove the temporary file
#     os.remove(temp_video_path)

#     return "processed_video.mp4"

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # Path to the Excel file
# excel_file_path = "Book1.xlsx"

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     if processed_video_path:
#         st.video(processed_video_path)













# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd
# import tempfile

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_file.write(video_bytes)
#         temp_video_path = temp_video_file.name

#     # Capture video from the temporary file
#     video = cv2.VideoCapture(temp_video_path)

#     # Ensure video is opened
#     if not video.isOpened():
#         st.error("Error opening video file.")
#         return None

#     # Get frame width, height, and FPS
#     frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
#     frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = video.get(cv2.CAP_PROP_FPS)

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as processed_video_file:
#         processed_video_path = processed_video_file.name

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(processed_video_path, fourcc, fps, (frame_width, frame_height))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.warning("End of video reached.")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     return processed_video_path

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # Path to the Excel file
# excel_file_path = "Book1.xlsx"

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     if processed_video_path is not None:
#         # Display the processed video
#         st.video(processed_video_path)











# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd
# import os

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     temp_video_path = "temp_video.mp4"
#     with open(temp_video_path, "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture(temp_video_path)

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     # Remove the temporary file
#     os.remove(temp_video_path)

#     return "processed_video.mp4"

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # Path to the Excel file
# excel_file_path = "Book1.xlsx"

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     st.video(processed_video_path)













# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     with open("temp_video.mp4", "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture("temp_video.mp4")

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     return "processed_video.mp4"

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # Path to the Excel file
# excel_file_path = "Book1.xlsx"

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     st.video(processed_video_path)












# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file_path):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file_path)
#     df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

#     if 'ImagePath' not in df.columns or 'Name' not in df.columns:
#         st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
#         return known_face_encodings, known_face_names

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     with open("temp_video.mp4", "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture("temp_video.mp4")

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # Path to the Excel file
# excel_file_path = "Book1.xlsx"

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     st.video('processed_video.mp4')












# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd

# # Load known faces and their names from an Excel file
# def load_known_faces_from_excel(excel_file):
#     known_face_encodings = []
#     known_face_names = []

#     df = pd.read_excel(excel_file)

#     for index, row in df.iterrows():
#         image_path = row['ImagePath']
#         name = row['Name']

#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(name)
#         else:
#             st.warning(f"No faces found in image {image_path}")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     with open("temp_video.mp4", "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture("temp_video.mp4")

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # GUI file uploader for Excel file
# excel_file = st.file_uploader("Choose an Excel file...", type=["xlsx"])

# # Load known faces
# if excel_file is not None:
#     known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file)

#     # Start face recognition when a video file is uploaded
#     if uploaded_file is not None:
#         video_face_detection(uploaded_file, known_face_encodings, known_face_names)
        
#         # Display the processed video
#         st.video('processed_video.mp4')
# else:
#     st.warning("Please upload an Excel file with known faces information.")


















# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition

# # Load known faces and their names
# def load_known_faces():
#     known_face_encodings = []
#     known_face_names = []

#     # Load the first image and learn how to recognize it.
#     image1 = face_recognition.load_image_file("modi.jpg")
#     encodings1 = face_recognition.face_encodings(image1)
#     if encodings1:
#         known_face_encodings.append(encodings1[0])
#         known_face_names.append("Narendra Modi")
#     else:
#         st.warning("No faces found in image modi.jpg")

#     # Load the second image and learn how to recognize it.
#     image2 = face_recognition.load_image_file("putin.jpeg")
#     encodings2 = face_recognition.face_encodings(image2)
#     if encodings2:
#         known_face_encodings.append(encodings2[0])
#         known_face_names.append("Putin")
#     else:
#         st.warning("No faces found in image putin.jpeg")

#     # Load the third image and learn how to recognize it.
#     image3 = face_recognition.load_image_file("zelensky.jpg")
#     encodings3 = face_recognition.face_encodings(image3)
#     if encodings3:
#         known_face_encodings.append(encodings3[0])
#         known_face_names.append("Zelensky")
#     else:
#         st.warning("No faces found in image zelensky.jpg")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     with open("temp_video.mp4", "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture("temp_video.mp4")

#     # Check if the video capture has been initialized correctly
#     if not video.isOpened():
#         st.error("Error: Could not open video file.")
#         return

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.info("End of video reached or failed to capture video.")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces()

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     st.video('processed_video.mp4')











# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition

# # Load known faces and their names
# def load_known_faces():
#     known_face_encodings = []
#     known_face_names = []

#     # Load the first image and learn how to recognize it.
#     image1 = face_recognition.load_image_file("modi.jpg")
#     encodings1 = face_recognition.face_encodings(image1)
#     if encodings1:
#         known_face_encodings.append(encodings1[0])
#         known_face_names.append("Narendra modi")
#     else:
#         st.warning("No faces found in image modi.jpg")

#     # Load the second image and learn how to recognize it.
#     image2 = face_recognition.load_image_file("putin.jpeg")
#     encodings2 = face_recognition.face_encodings(image2)
#     if encodings2:
#         known_face_encodings.append(encodings2[0])
#         known_face_names.append("Putin")
#     else:
#         st.warning("No faces found in image another_person.jpg")

#     # Load the third image and learn how to recognize it.
#     image3 = face_recognition.load_image_file("zelensky.jpg")
#     encodings3 = face_recognition.face_encodings(image3)
#     if encodings3:
#         known_face_encodings.append(encodings3[0])
#         known_face_names.append("zelensky")
#     else:
#         st.warning("No faces found in image third_person.jpg")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     with open("temp_video.mp4", "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture("temp_video.mp4")

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces()

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     st.video('processed_video.mp4')

















# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition

# # Load known faces and their names
# def load_known_faces():
#     known_face_encodings = []
#     known_face_names = []

#     # Load the first image and learn how to recognize it.
#     image1 = face_recognition.load_image_file("modi.jpg")
#     encodings1 = face_recognition.face_encodings(image1)
#     if encodings1:
#         known_face_encodings.append(encodings1[0])
#         known_face_names.append("Narendra Modi")
#     else:
#         st.warning("No faces found in image modi.jpg")

#     # Load the second image and learn how to recognize it.
#     image2 = face_recognition.load_image_file("putin.jpeg")
#     encodings2 = face_recognition.face_encodings(image2)
#     if encodings2:
#         known_face_encodings.append(encodings2[0])
#         known_face_names.append("Putin")
#     else:
#         st.warning("No faces found in image another_person.jpg")

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     with open("temp_video.mp4", "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture("temp_video.mp4")

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces()

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     st.video('processed_video.mp4')















# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition

# # Load known faces and their names
# def load_known_faces():
#     known_face_encodings = []
#     known_face_names = []

#     # Load a sample picture and learn how to recognize it.
#     # Add your own images here, with appropriate encoding and name.
#     image = face_recognition.load_image_file("modi.jpg")
#     encoding = face_recognition.face_encodings(image)[0]
#     known_face_encodings.append(encoding)
#     known_face_names.append("Narendra modi")

#     # Repeat the above steps for additional known faces
#     # ...

#     return known_face_encodings, known_face_names

# # Function to detect faces in video frames and recognize them
# def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()

#     # Write the byte array to a temporary file
#     with open("temp_video.mp4", "wb") as f:
#         f.write(video_bytes)

#     # Capture video from the temporary file
#     video = cv2.VideoCapture("temp_video.mp4")

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break

#         # Convert the frame from BGR to RGB (face_recognition uses RGB)
#         rgb_frame = frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face in this frame of video
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # See if the face is a match for any known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#             name = "Unknown"

#             # If a match was found in known_face_encodings, use the first one.
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Write the frame with recognized faces to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

# # Streamlit app
# st.title("Video Face Recognition App")
# st.write("Upload a video file and the app will recognize faces.")

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Load known faces
# known_face_encodings, known_face_names = load_known_faces()

# # Start face recognition when a video file is uploaded
# if uploaded_file is not None:
#     video_face_detection(uploaded_file, known_face_encodings, known_face_names)
    
#     # Display the processed video
#     st.video('processed_video.mp4')











# import streamlit as st
# import cv2
# import numpy as np

# # Function to detect faces in video frames
# def video_face_detection(uploaded_file):
#     stframe = st.empty()
    
#     # Convert the uploaded file to a byte array
#     video_bytes = uploaded_file.read()
    
#     # Write the byte array to a temporary file
#     with open("temp_video.mp4", "wb") as f:
#         f.write(video_bytes)
    
#     # Capture video from the temporary file
#     video = cv2.VideoCapture("temp_video.mp4")
    
#     # Load the Haar Cascade Classifier for face detection
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(video.get(3)), int(video.get(4))))

#     # Continuously process video feed and display in window until the end of the video
#     while video.isOpened():
#         check, frame = video.read()
#         if not check:
#             st.error("Failed to capture video or end of video reached")
#             break
        
#         # Grayscale conversion of the frame
#         gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
#         # Detect faces
#         faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.05, minNeighbors=5)
        
#         # Draw rectangles around detected faces
#         for (x, y, w, h) in faces:
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
#         # Write the frame with rectangles to the output video
#         out.write(frame)
        
#         # Display the processed image
#         stframe.image(frame, channels="BGR")
    
#     # Release the video capture and writer
#     video.release()
#     out.release()

# # Streamlit app
# st.title("Video Face Detection App")
# st.write("Upload a video file and the app will detect faces.")

# # GUI file uploader for video file
# uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

# # Start face detection when a video file is uploaded
# if uploaded_file is not None:
#     video_face_detection(uploaded_file)
    
#     # Display the processed video
#     st.video('processed_video.mp4')















# import cv2
# import mediapipe as mp
# import streamlit as st
# import tempfile
# import face_recognition
# import numpy as np
# from PIL import Image

# # Define a function to load and convert image to RGB
# def load_image_as_rgb(image_path):
#     try:
#         image = Image.open(image_path).convert('RGB')
#         return np.array(image)
#     except Exception as e:
#         print(f"Error loading image: {e}")
#         raise

# # Load Narendra Modi's face encoding (replace with your actual encoding)
# def load_modi_encoding():
#     try:
#         modi_image = load_image_as_rgb("modi.jpg")
#         # Debug print to check the type and shape of the image
#         print(f"Modi image dtype: {modi_image.dtype}, shape: {modi_image.shape}")
#         if modi_image.ndim != 3 or modi_image.shape[2] != 3:
#             raise ValueError("Error: Modi image is not in the expected RGB format.")
#         return face_recognition.face_encodings(modi_image)[0]
#     except ValueError as e:
#         st.error(f"ValueError: {e}")
#         raise

# # Initialize Modi's face encoding
# try:
#     modi_face_encoding = load_modi_encoding()
# except Exception as e:
#     st.error(f"Exception: {e}")
#     raise

# # Initialize MediaPipe Face Detection
# mp_face_detection = mp.solutions.face_detection

# # Streamlit app
# st.title("Face Detection and Recognition in Video")
# st.write("Upload a video file to detect and recognize faces.")

# # File uploader
# uploaded_file = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])

# if uploaded_file is not None:
#     # Save uploaded file to a temporary file
#     tfile = tempfile.NamedTemporaryFile(delete=False)
#     tfile.write(uploaded_file.read())
#     tfile.close()  # Ensure the file is closed before reopening it
    
#     # Open the video file
#     video_capture = cv2.VideoCapture(tfile.name)

#     # Check if video opened successfully
#     if not video_capture.isOpened():
#         st.error("Error: Could not open video.")
#     else:
#         # Get video writer setup to save the output
#         fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         fps = int(video_capture.get(cv2.CAP_PROP_FPS))
#         width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         out_file = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')
#         out_file.close()  # Ensure the file is closed before reopening it for writing
#         out = cv2.VideoWriter(out_file.name, fourcc, fps, (width, height))

#         # Initialize face detection
#         with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
#             while video_capture.isOpened():
#                 ret, frame = video_capture.read()
#                 if not ret:
#                     break

#                 # Convert the BGR image to RGB
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#                 # Debug print to confirm image dtype and shape
#                 print(f"Frame dtype: {rgb_frame.dtype}, shape: {rgb_frame.shape}")

#                 # Ensure the image is in the correct format
#                 if rgb_frame.ndim != 3 or rgb_frame.shape[2] != 3:
#                     st.error("Error: Frame is not in the expected RGB format.")
#                     continue

#                 # Find all face locations and face encodings in the frame
#                 try:
#                     face_locations = face_recognition.face_locations(rgb_frame)
#                     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#                 except RuntimeError as e:
#                     st.error(f"RuntimeError: {e}")
#                     continue

#                 # Iterate through each face found in the frame
#                 for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                     # Draw the rectangle around the face
#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#                     # Draw the label
#                     label = "Unknown"
#                     if face_recognition.compare_faces([modi_face_encoding], face_encoding)[0]:
#                         label = "Narendra Modi"
#                     cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#                 # Write the annotated frame to the output video
#                 out.write(frame)

#         # Release handle to the video
#         video_capture.release()
#         out.release()
        
#         # Display the output video
#         st.video(out_file.name)

#         # Clean up temporary files
#         # Uncomment these lines if you want to remove the temporary files after processing
#         # os.remove(tfile.name)
#         # os.remove(out_file.name)

















# import cv2
# import mediapipe as mp
# import streamlit as st
# import tempfile
# import face_recognition
# import numpy as np
# from PIL import Image

# # Define a function to load and convert image to RGB
# def load_image_as_rgb(image_path):
#     image = Image.open(image_path).convert('RGB')
#     return np.array(image)

# # Load Narendra Modi's face encoding (replace with your actual encoding)
# def load_modi_encoding():
#     modi_image = load_image_as_rgb("modi.jpg")
#     # Debug print to check the type and shape of the image
#     print(f"Modi image dtype: {modi_image.dtype}, shape: {modi_image.shape}")
#     if modi_image.ndim != 3 or modi_image.shape[2] != 3:
#         raise ValueError("Error: Modi image is not in the expected RGB format.")
#     return face_recognition.face_encodings(modi_image)[0]

# # Initialize Modi's face encoding
# try:
#     modi_face_encoding = load_modi_encoding()
# except ValueError as e:
#     st.error(f"ValueError: {e}")
#     raise

# # Initialize MediaPipe Face Detection
# mp_face_detection = mp.solutions.face_detection

# # Streamlit app
# st.title("Face Detection and Recognition in Video")
# st.write("Upload a video file to detect and recognize faces.")

# # File uploader
# uploaded_file = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])

# if uploaded_file is not None:
#     # Save uploaded file to a temporary file
#     tfile = tempfile.NamedTemporaryFile(delete=False)
#     tfile.write(uploaded_file.read())
#     tfile.close()  # Ensure the file is closed before reopening it
    
#     # Open the video file
#     video_capture = cv2.VideoCapture(tfile.name)

#     # Check if video opened successfully
#     if not video_capture.isOpened():
#         st.error("Error: Could not open video.")
#     else:
#         # Get video writer setup to save the output
#         fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         fps = int(video_capture.get(cv2.CAP_PROP_FPS))
#         width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         out_file = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')
#         out_file.close()  # Ensure the file is closed before reopening it for writing
#         out = cv2.VideoWriter(out_file.name, fourcc, fps, (width, height))

#         # Initialize face detection
#         with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
#             while video_capture.isOpened():
#                 ret, frame = video_capture.read()
#                 if not ret:
#                     break

#                 # Convert the BGR image to RGB
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#                 # Debug print to confirm image dtype and shape
#                 print(f"Frame dtype: {rgb_frame.dtype}, shape: {rgb_frame.shape}")

#                 # Ensure the image is in the correct format
#                 if rgb_frame.ndim != 3 or rgb_frame.shape[2] != 3:
#                     st.error("Error: Frame is not in the expected RGB format.")
#                     continue

#                 # Find all face locations and face encodings in the frame
#                 try:
#                     face_locations = face_recognition.face_locations(rgb_frame)
#                     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#                 except RuntimeError as e:
#                     st.error(f"RuntimeError: {e}")
#                     continue

#                 # Iterate through each face found in the frame
#                 for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                     # Draw the rectangle around the face
#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#                     # Draw the label
#                     label = "Unknown"
#                     if face_recognition.compare_faces([modi_face_encoding], face_encoding)[0]:
#                         label = "Narendra Modi"
#                     cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#                 # Write the annotated frame to the output video
#                 out.write(frame)

#         # Release handle to the video
#         video_capture.release()
#         out.release()
        
#         # Display the output video
#         st.video(out_file.name)

#         # Clean up temporary files
#         # Uncomment these lines if you want to remove the temporary files after processing
#         # os.remove(tfile.name)
#         # os.remove(out_file.name)
# import cv2
# import mediapipe as mp
# import streamlit as st
# import tempfile
# import face_recognition
# import numpy as np
# from PIL import Image

# # Define a function to load and convert image to RGB
# def load_image_as_rgb(image_path):
#     image = Image.open(image_path).convert('RGB')
#     return np.array(image)

# # Load Narendra Modi's face encoding (replace with your actual encoding)
# def load_modi_encoding():
#     modi_image = load_image_as_rgb("modi.jpg")
#     # Debug print to check the type and shape of the image
#     print(f"Modi image dtype: {modi_image.dtype}, shape: {modi_image.shape}")
#     if modi_image.ndim != 3 or modi_image.shape[2] != 3:
#         raise ValueError("Error: Modi image is not in the expected RGB format.")
#     return face_recognition.face_encodings(modi_image)[0]

# # Initialize Modi's face encoding
# try:
#     modi_face_encoding = load_modi_encoding()
# except ValueError as e:
#     st.error(f"ValueError: {e}")
#     raise

# # Initialize MediaPipe Face Detection
# mp_face_detection = mp.solutions.face_detection

# # Streamlit app
# st.title("Face Detection and Recognition in Video")
# st.write("Upload a video file to detect and recognize faces.")

# # File uploader
# uploaded_file = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])

# if uploaded_file is not None:
#     # Save uploaded file to a temporary file
#     tfile = tempfile.NamedTemporaryFile(delete=False)
#     tfile.write(uploaded_file.read())
#     tfile.close()  # Ensure the file is closed before reopening it
    
#     # Open the video file
#     video_capture = cv2.VideoCapture(tfile.name)

#     # Check if video opened successfully
#     if not video_capture.isOpened():
#         st.error("Error: Could not open video.")
#     else:
#         # Get video writer setup to save the output
#         fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         fps = int(video_capture.get(cv2.CAP_PROP_FPS))
#         width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         out_file = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')
#         out_file.close()  # Ensure the file is closed before reopening it for writing
#         out = cv2.VideoWriter(out_file.name, fourcc, fps, (width, height))

#         # Initialize face detection
#         with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
#             while video_capture.isOpened():
#                 ret, frame = video_capture.read()
#                 if not ret:
#                     break

#                 # Convert the BGR image to RGB
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#                 # Debug print to confirm image dtype and shape
#                 print(f"Frame dtype: {rgb_frame.dtype}, shape: {rgb_frame.shape}")

#                 # Ensure the image is in the correct format
#                 if rgb_frame.ndim != 3 or rgb_frame.shape[2] != 3:
#                     st.error("Error: Frame is not in the expected RGB format.")
#                     continue

#                 # Find all face locations and face encodings in the frame
#                 try:
#                     face_locations = face_recognition.face_locations(rgb_frame)
#                     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#                 except RuntimeError as e:
#                     st.error(f"RuntimeError: {e}")
#                     continue

#                 # Iterate through each face found in the frame
#                 for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                     # Draw the rectangle around the face
#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#                     # Draw the label
#                     label = "Unknown"
#                     if face_recognition.compare_faces([modi_face_encoding], face_encoding)[0]:
#                         label = "Narendra Modi"
#                     cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#                 # Write the annotated frame to the output video
#                 out.write(frame)

#         # Release handle to the video
#         video_capture.release()
#         out.release()
        
#         # Display the output video
#         st.video(out_file.name)

#         # Clean up temporary files
#         # Uncomment these lines if you want to remove the temporary files after processing
#         # os.remove(tfile.name)
#         # os.remove(out_file.name)















# import cv2
# import mediapipe as mp
# import streamlit as st
# import tempfile
# import numpy as np

# # Initialize MediaPipe Face Detection
# mp_face_detection = mp.solutions.face_detection

# # Streamlit app
# st.title("Face Detection in Video")
# st.write("Upload a video file to detect faces.")

# # File uploader
# uploaded_file = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])

# if uploaded_file is not None:
#     # Save uploaded file to a temporary file
#     tfile = tempfile.NamedTemporaryFile(delete=False)
#     tfile.write(uploaded_file.read())
#     tfile.close()  # Ensure the file is closed before reopening it

#     # Open the video file
#     video_capture = cv2.VideoCapture(tfile.name)

#     # Check if video opened successfully
#     if not video_capture.isOpened():
#         st.error("Error: Could not open video.")
#     else:
#         # Get video writer setup to save the output
#         fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         fps = int(video_capture.get(cv2.CAP_PROP_FPS))
#         width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         out_file = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')
#         out_file.close()  # Ensure the file is closed before reopening it for writing
#         out = cv2.VideoWriter(out_file.name, fourcc, fps, (width, height))

#         # Initialize face detection
#         with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
#             while video_capture.isOpened():
#                 ret, frame = video_capture.read()
#                 if not ret:
#                     break

#                 # Convert the BGR image to RGB
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#                 # Debug print to confirm image dtype and shape
#                 print(f"Frame dtype: {rgb_frame.dtype}, shape: {rgb_frame.shape}")

#                 # Ensure the image is in the correct format
#                 if rgb_frame.ndim != 3 or rgb_frame.shape[2] != 3:
#                     st.error("Error: Frame is not in the expected RGB format.")
#                     continue

#                 # Find face locations using MediaPipe
#                 results = face_detection.process(rgb_frame)

#                 if results.detections:
#                     for detection in results.detections:
#                         bboxC = detection.location_data.relative_bounding_box
#                         ih, iw, _ = frame.shape
#                         x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                        
#                         # Draw bounding box on the frame
#                         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#                 # Write the annotated frame to the output video
#                 out.write(frame)

#         # Release handle to the video
#         video_capture.release()
#         out.release()

#         # Display the output video
#         st.video(out_file.name)

#         # Clean up temporary files
#         # Uncomment these lines if you want to remove the temporary files after processing
#         # os.remove(tfile.name)
#         # os.remove(out_file.name)
