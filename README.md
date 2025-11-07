# ASL Sentence Builder

Real-time American Sign Language (ASL) recognition and sentence construction using computer vision and deep learning.

---

## 🚀 Project Overview
This project enables users to spell out words and build sentences in real time using American Sign Language gestures, captured via webcam. The system recognizes hand signs, constructs words and sentences, and can even speak them aloud using text-to-speech.

---

## ✨ Features
- Real-time ASL alphabet recognition from webcam
- Sentence and word construction with manual control
- Text-to-speech for recognized words and sentences
- Clean, minimal interface for easy demo and presentation

---

## 📸 Demo

### Video Demo

[![Watch the demo](assets/image1.jpg)](assets/demo.mp4)

### Screenshots
| ASL Recognition | Word Building | Letter Detection | ASL Alphabet Reference |
|:--------------:|:-------------:|:----------------:|:---------------------:|
| ![](assets/image1.jpg) | ![](assets/image2.jpg) | ![](assets/image3.jpg) | ![](assets/image4.jpg) |

---

## 🛠️ Setup & Installation
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd American-Sign-Language-Detection
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 💡 Usage

### Local OpenCV Demo
- Run the main script:
  ```bash
  python Onworking.py
  ```
- Show ASL gestures to your webcam.
- Press `SPACE` to complete a word, `ENTER` to complete a sentence, and `ESC` to exit.
- The recognized text will be displayed and spoken aloud.

### Streamlit Demo
- Ensure you are using Python 3.10 or 3.11 for MediaPipe compatibility.
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Launch the interactive web app:
  ```bash
  streamlit run streamlit_app.py
  ```
- Click **Start** in the WebRTC widget to enable your webcam, then use the on-screen controls to manage words and sentences. The **Speak sentence** button plays synthesized audio in the browser.

---

## 🙌 Acknowledgements
- [MediaPipe](https://mediapipe.dev/)
- [gTTS](https://pypi.org/project/gTTS/)
- [OpenCV](https://opencv.org/)

---

## 📂 Assets
- Demo video in `assets/demo.mp4`.
- Demo images as `assets/image1.jpg`, `assets/image2.jpg`, `assets/image3.jpg`, `assets/image4.jpg`.

---

> **Made with ❤️ for accessible communication.**

