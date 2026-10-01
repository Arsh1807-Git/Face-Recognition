# Live Face Recognition with Firebase Database

Detects faces via webcam, matches them against previously stored faces,
and auto-registers new faces (name, age, gender) into a live Firebase
(Firestore) database.

## Project Structure
```
Face-Recognition/
├── main.py             # Webcam loop, detection, matching, UI
├── database.py         # All Firestore read/write logic
├── firebase_config.py  # Firebase Admin SDK setup
├── requirements.txt
├── .gitignore
└── README.md
```

## Step 1: Install Python prerequisites

`face_recognition` depends on `dlib`, which needs a C++ build toolchain
and CMake to compile. Install these BEFORE running `pip install`.

**Windows:**
1. Install [CMake](https://cmake.org/download/) and check "Add to PATH" during install.
2. Install "Desktop development with C++" via the
   [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
3. Restart your terminal after both installs.

**macOS:**
```bash
brew install cmake
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install cmake build-essential python3-dev
```

## Step 2: Set up a virtual environment and install packages

```bash
cd face_recognition_project
python -m venv venv
```

### Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

> `dlib` can take 5–15 minutes to compile the first time. This is normal.
> If it fails on Windows, try `pip install cmake` first, then retry.
## Step 3: Set up Firebase (Firestore)

1. Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. In the left sidebar, click **Build → Firestore Database → Create database**.
   Choose "Start in test mode" for now (fine for development).
3. Click the gear icon → **Project settings → Service accounts** tab.
4. Click **Generate new private key** — this downloads a `.json` file.
5. Rename that file to `serviceAccountKey.json` and place it directly
   inside the `face_recognition_project` folder (same level as `main.py`).
6. **Important:** never upload this file to a public GitHub repo — it's
   a secret credential. Add it to `.gitignore`.

## Step 4: Run the project

```bash
python main.py
```

- A window opens showing your webcam feed.
- Any face detected gets a colored box:
  - **Red box "New Face"** → not in the database yet.
  - **Green box** → matched, shows stored `name | age | gender`.
- While a red box is showing, press **`n`** in the video window, then
  switch to your terminal — it will ask for Name, Age, and Gender.
  After you enter them, that face is saved to Firestore instantly and
  will show a green box from then on (even after restarting the app).
- Press **`q`** to quit.

## How matching actually works

Each face is converted into a 128-dimension numerical "encoding" by
`face_recognition` (a dlib deep-learning model under the hood). Two
photos of the same person produce very similar encodings; different
people produce very different ones. `MATCH_TOLERANCE = 0.6` in
`main.py` controls how similar two encodings must be to count as
"the same person" — lower it (e.g. `0.5`) for stricter matching if
you get false positives, raise it slightly if the same person isn't
being recognized consistently.

## Possible improvements (good talking points if this is a resume project)

- Add a simple GUI (Tkinter/PyQt) instead of terminal `input()` for
  registering new faces.
- Store a cropped face photo in Firebase Storage alongside the record.
- Add a "confidence score" display next to recognized names.
- Deploy as a small Flask/FastAPI web app with a live video stream
  instead of a local OpenCV window, so it can run on a server.
- Add authentication so only authorized users can view stored records.
