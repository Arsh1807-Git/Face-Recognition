"""
main.py
-------
Run this file to start the live face recognition system.

Flow per frame:
1. Capture frame from webcam.
2. Detect all faces in the frame + compute their encodings.
3. For each face, compare it against every known encoding in memory.
4. If a match is found -> draw a GREEN box + show stored name/age/gender,
   and update "last_seen" in Firestore.
5. If no match is found -> draw a RED box + "New Face". Press 'n' to
   pause and register that person's details on the spot.

Controls while the window is focused:
    q  -> quit the program
    n  -> register the most recently detected NEW (unmatched) face
"""

import cv2
import face_recognition
import numpy as np

from database import load_all_faces, add_new_face, update_last_seen

# How strict the matching is. Lower = stricter (fewer false matches).
# 0.6 is the commonly recommended default for face_recognition.
MATCH_TOLERANCE = 0.6

# Shrinking the frame before processing makes detection much faster.
# 0.25 = process at 1/4 resolution, then scale coordinates back up.
FRAME_RESIZE_SCALE = 0.25


def get_face_details_from_user():
    """
    Prompts in the terminal for a new person's details.
    Keeps asking for age until a valid number is entered.
    """
    print("\n--- New face detected! Please enter their details ---")
    name = input("Name: ").strip() or "Unknown"

    while True:
        age_input = input("Age: ").strip()
        if age_input.isdigit():
            age = int(age_input)
            break
        print("Please enter a valid number for age.")

    gender = input("Gender: ").strip() or "Unknown"
    print("--- Saving to database... ---\n")
    return name, age, gender


def main():
    print("Loading known faces from Firestore...")
    known_encodings, known_ids, known_details = load_all_faces()
    print(f"Loaded {len(known_encodings)} known face(s).\n")

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("ERROR: Could not access the webcam.")
        return

    # Keeps track of the encoding of a currently-unrecognized face so
    # that pressing 'n' knows exactly which face to register.
    pending_new_encoding = None

    print("Starting camera. Press 'q' to quit, 'n' to register a new face.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame from webcam.")
            break

        # Resize for faster processing, then convert BGR (OpenCV) -> RGB
        # (face_recognition expects RGB images).
        small_frame = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE_SCALE, fy=FRAME_RESIZE_SCALE)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        pending_new_encoding = None  # reset each frame

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Scale face location coordinates back up to full frame size
            top = int(top / FRAME_RESIZE_SCALE)
            right = int(right / FRAME_RESIZE_SCALE)
            bottom = int(bottom / FRAME_RESIZE_SCALE)
            left = int(left / FRAME_RESIZE_SCALE)

            label = "New Face"
            box_color = (0, 0, 255)  # red (BGR)

            if known_encodings:
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_index = int(np.argmin(face_distances))

                if face_distances[best_match_index] <= MATCH_TOLERANCE:
                    details = known_details[best_match_index]
                    matched_id = known_ids[best_match_index]

                    label = f"{details['name']} | {details['age']} | {details['gender']}"
                    box_color = (0, 200, 0)  # green (BGR)

                    update_last_seen(matched_id)
                else:
                    pending_new_encoding = face_encoding
            else:
                pending_new_encoding = face_encoding

            # Draw the box and label on the full-size frame
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.rectangle(frame, (left, bottom - 25), (right, bottom), box_color, cv2.FILLED)
            cv2.putText(frame, label, (left + 4, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        cv2.putText(frame, "Press 'n' to register new face | 'q' to quit",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 1)

        cv2.imshow("Face Recognition System", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        if key == ord('n'):
            if pending_new_encoding is not None:
                name, age, gender = get_face_details_from_user()
                new_id = add_new_face(pending_new_encoding, name, age, gender)

                # Add to in-memory lists immediately so it's recognized
                # on the very next frame without restarting the app.
                known_encodings.append(pending_new_encoding)
                known_ids.append(new_id)
                known_details.append({"name": name, "age": age, "gender": gender})

                print(f"Saved '{name}' to database with ID: {new_id}\n")
            else:
                print("No new/unmatched face currently in frame to register.")

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
