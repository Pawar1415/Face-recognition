# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import pandas as pd
# import os
# import tempfile
# from dotenv import load_dotenv
# import yt_dlp

# # Load environment variables from .env file
# load_dotenv()

# # Get the file path from environment variables
# excel_file_path = os.getenv('EXCEL_FILE_PATH')

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

# # Download video using yt-dlp
# def download_video_from_youtube(youtube_url):
#     ydl_opts = {
#         'format': 'bestvideo+bestaudio/best',
#         'outtmpl': tempfile.mktemp(suffix=".mp4"),  # Temporary file
#         'noplaylist': True,
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info_dict = ydl.extract_info(youtube_url, download=True)
#         video_file_path = ydl.prepare_filename(info_dict)
    
#     return video_file_path

# # Function to detect faces in video frames and recognize them
# def video_face_detection(video_file_path, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Create temporary file paths
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     # Capture video from the downloaded file
#     video = cv2.VideoCapture(video_file_path)

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

#     return output_video_path

# # Streamlit app
# def run_streamlit_app():
#     st.title("Video Face Recognition App")
#     st.write("Provide a YouTube URL and the app will recognize faces in the video.")

#     # Load known faces
#     known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

#     # GUI text input for YouTube URL
#     youtube_url = st.text_input("Enter YouTube URL")

#     # Start face recognition when a YouTube URL is provided
#     if youtube_url:
#         video_file_path = download_video_from_youtube(youtube_url)
#         processed_video_path = video_face_detection(video_file_path, known_face_encodings, known_face_names)

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
# from dotenv import load_dotenv
# import yt_dlp
# import easyocr

# # Load environment variables from .env file
# load_dotenv()

# # Get the file path from environment variables
# excel_file_path = os.getenv('EXCEL_FILE_PATH')

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

# # Download video from YouTube URL using yt_dlp
# def download_video_from_youtube(youtube_url):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#         temp_video_path = temp_video_file.name

#     ydl_opts = {
#         'format': 'best',
#         'outtmpl': temp_video_path,
#         'quiet': True,
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([youtube_url])

#     return temp_video_path

# # Function to detect faces and license plates in video frames
# def video_detection(video_path, known_face_encodings, known_face_names):
#     stframe = st.empty()

#     # Create temporary file path for output video
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
#         output_video_path = temp_output_file.name

#     # Capture video from the given path
#     video = cv2.VideoCapture(video_path)

#     # Check if video opened successfully
#     if not video.isOpened():
#         st.error("Error: Could not open video.")
#         return None

#     # Create a VideoWriter object to save the processed video
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader

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

#         # Detect license plates using EasyOCR
#         results = reader.readtext(frame)

#         for (bbox, text, prob) in results:
#             if prob > 0.5:  # Confidence threshold
#                 (top_left, top_right, bottom_right, bottom_left) = bbox
#                 top_left = tuple(map(int, top_left))
#                 bottom_right = tuple(map(int, bottom_right))

#                 # Draw the bounding box and the detected text
#                 cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 3)
#                 cv2.putText(frame, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#         # Write the frame with recognized faces and license plates to the output video
#         out.write(frame)

#         # Display the processed image
#         stframe.image(frame, channels="BGR")

#     # Release the video capture and writer
#     video.release()
#     out.release()

#     return output_video_path

# # Streamlit app
# def run_streamlit_app():
#     st.title("Video Face & License Plate Recognition App")
#     st.write("Provide a YouTube URL and the app will recognize faces and detect license plates.")

#     # Load known faces
#     known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

#     # Input for YouTube URL
#     youtube_url = st.text_input("Enter YouTube URL:")

#     # Start detection when a YouTube URL is provided
#     if youtube_url:
#         st.write("Downloading video...")
#         video_path = download_video_from_youtube(youtube_url)
#         st.write("Video downloaded. Processing...")

#         processed_video_path = video_detection(video_path, known_face_encodings, known_face_names)
        
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
















import streamlit as st
import cv2
import numpy as np
import face_recognition
import pandas as pd
import os
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the file path from environment variables
excel_file_path = os.getenv('EXCEL_FILE_PATH')

# Load known faces and their names from an Excel file
def load_known_faces_from_excel(excel_file_path):
    known_face_encodings = []
    known_face_names = []

    df = pd.read_excel(excel_file_path)
    df.columns = [col.strip() for col in df.columns]  # Strip any extra spaces in the column names

    if 'ImagePath' not in df.columns or 'Name' not in df.columns:
        st.error("The Excel file must contain 'ImagePath' and 'Name' columns.")
        return known_face_encodings, known_face_names

    for index, row in df.iterrows():
        image_path = row['ImagePath']
        name = row['Name']

        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(name)
        else:
            st.warning(f"No faces found in image {image_path}")

    return known_face_encodings, known_face_names

# Function to detect faces in video frames and recognize them
def video_face_detection(uploaded_file, known_face_encodings, known_face_names):
    stframe = st.empty()

    # Create temporary file paths
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_path = temp_video_file.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
        output_video_path = temp_output_file.name

    # Write the uploaded video to a temporary file
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Capture video from the temporary file
    video = cv2.VideoCapture(temp_video_path)

    # Check if video opened successfully
    if not video.isOpened():
        st.error("Error: Could not open video.")
        return None

    # Create a VideoWriter object to save the processed video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    # Continuously process video feed and display in window until the end of the video
    while video.isOpened():
        check, frame = video.read()
        if not check:
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

        # Write the frame with recognized faces to the output video
        out.write(frame)

        # Display the processed image
        stframe.image(frame, channels="BGR")

    # Release the video capture and writer
    video.release()
    out.release()

    # Remove the temporary input file
    os.remove(temp_video_path)

    return output_video_path

# Streamlit app
def run_streamlit_app():
    st.title("Video Face Recognition App")
    st.write("Upload a video file and the app will recognize faces.")

    # Load known faces
    known_face_encodings, known_face_names = load_known_faces_from_excel(excel_file_path)

    # GUI file uploader for video file
    uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

    # Start face recognition when a video file is uploaded
    if uploaded_file is not None:
        processed_video_path = video_face_detection(uploaded_file, known_face_encodings, known_face_names)
        
        # Display the processed video and add download button
        if processed_video_path:
            st.video(processed_video_path)
            
            # Provide a download link for the processed video
            with open(processed_video_path, "rb") as video_file:
                video_bytes = video_file.read()
                st.download_button(
                    label="Download Processed Video",
                    data=video_bytes,
                    file_name="processed_video.mp4",
                    mime="video/mp4"
                )

if __name__ == "__main__":
    run_streamlit_app()






















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
#     excel_file_path = "source/Book1.xlsx"

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