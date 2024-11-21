









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













# from fastapi import FastAPI, UploadFile, File, HTTPException
# import face_recognition
# import pandas as pd
# import cv2
# import os
# import tempfile

# app = FastAPI()

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
