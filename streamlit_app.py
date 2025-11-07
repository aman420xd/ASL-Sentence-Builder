import copy
import time
from io import BytesIO

import av
import cv2 as cv
import mediapipe as mp
import numpy as np
import streamlit as st
from gtts import gTTS
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer

from model.keypoint_classifier.keypoint_classifier import KeyPointClassifier
from OnWorking import (
    calc_bounding_rect,
    calc_landmark_list,
    draw_bounding_rect,
    draw_info_text,
    draw_landmarks,
    pre_process_landmark,
)


REQUIRED_CONSECUTIVE_FRAMES = 25
INPUT_COOLDOWN_SECONDS = 0.3


@st.cache_resource
def load_labels():
    with open(
        "model/keypoint_classifier/keypoint_classifier_label.csv",
        encoding="utf-8-sig",
    ) as f:
        return [row.strip() for row in f if row.strip()]


def synthesize_audio(text: str) -> BytesIO:
    buffer = BytesIO()
    tts = gTTS(text=text, lang="en")
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer


class ASLStreamProcessor(VideoTransformerBase):
    def __init__(self):
        self.labels = load_labels()
        self.classifier = KeyPointClassifier()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )

        self.current_gesture = None
        self.last_character = ""
        self.consecutive_frames = 0
        self.input_cooldown_until = 0.0

        self.current_word = []
        self.sentence_parts = []

        self.debug_text = ""

    def _append_letter(self, gesture: str):
        self.current_word.append(gesture)
        self.last_character = gesture
        self.debug_text = f"Letter: {gesture}, Word: {''.join(self.current_word)}"

    def complete_word(self):
        if self.current_word:
            word = "".join(self.current_word)
            self.sentence_parts.append(word)
            self.current_word = []
            self.last_character = ""
            return word
        return ""

    def remove_last_letter(self):
        if self.current_word:
            self.current_word.pop()
        self.last_character = ""

    def clear_sentence(self):
        self.current_word = []
        self.sentence_parts = []
        self.last_character = ""

    def get_sentence(self) -> str:
        joined = " ".join(self.sentence_parts)
        if self.current_word:
            joined = f"{joined} {''.join(self.current_word)}".strip()
        return joined

    def transform(self, frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        debug_image = copy.deepcopy(image)

        rgb_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        results = self.hands.process(rgb_image)

        current_time = time.time()

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, results.multi_handedness
            ):
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                processed = pre_process_landmark(landmark_list)
                gesture_id = self.classifier(processed)
                gesture = self.labels[gesture_id]

                if gesture == self.current_gesture:
                    self.consecutive_frames += 1
                else:
                    self.current_gesture = gesture
                    self.consecutive_frames = 1

                if (
                    self.consecutive_frames >= REQUIRED_CONSECUTIVE_FRAMES
                    and gesture != self.last_character
                    and current_time >= self.input_cooldown_until
                ):
                    self._append_letter(gesture)
                    self.input_cooldown_until = current_time + INPUT_COOLDOWN_SECONDS

                brect = calc_bounding_rect(debug_image, hand_landmarks)
                debug_image = draw_bounding_rect(True, debug_image, brect)
                debug_image = draw_landmarks(debug_image, landmark_list)
                debug_image = draw_info_text(
                    debug_image,
                    brect,
                    handedness,
                    f"{self.current_gesture or 'None'} ({self.consecutive_frames})",
                )
        else:
            self.current_gesture = None
            self.consecutive_frames = 0
            self.last_character = ""

        sentence_text = f"Sentence: {' '.join(self.sentence_parts)}"
        word_text = f"Current word: {''.join(self.current_word)}"

        cv.putText(
            debug_image,
            word_text,
            (20, debug_image.shape[0] - 50),
            cv.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2,
        )
        cv.putText(
            debug_image,
            sentence_text,
            (20, debug_image.shape[0] - 20),
            cv.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        return av.VideoFrame.from_ndarray(debug_image, format="bgr24")


def main():
    st.set_page_config(page_title="ASL Sentence Builder", layout="wide")
    st.title("ASL Sentence Builder – Streamlit")
    st.caption("Real-time ASL alphabet recognition with sentence construction")

    st.sidebar.header("Instructions")
    st.sidebar.write(
        "Raise a hand sign clearly within the webcam frame. The app adds a letter after it remains stable for a short duration."
    )
    st.sidebar.write("Use the buttons below the video to manage words and sentences.")

    rtc_ctx = webrtc_streamer(
        key="asl-stream",
        video_transformer_factory=ASLStreamProcessor,
        media_stream_constraints={"video": True, "audio": False},
    )

    col1, col2, col3 = st.columns(3)

    if rtc_ctx.video_transformer:
        processor: ASLStreamProcessor = rtc_ctx.video_transformer

        with col1:
            if st.button("Complete word", use_container_width=True):
                word = processor.complete_word()
                if word:
                    st.success(f"Word added: {word}")

            if st.button("Undo letter", use_container_width=True):
                processor.remove_last_letter()

        with col2:
            if st.button("Clear all", use_container_width=True):
                processor.clear_sentence()

            if st.button("Speak sentence", type="primary", use_container_width=True):
                sentence = processor.get_sentence()
                if sentence:
                    audio = synthesize_audio(sentence)
                    st.audio(audio, format="audio/mp3")
                else:
                    st.info("Nothing to speak yet.")

        with col3:
            st.subheader("Current text")
            st.write(f"**Word:** {' '.join(processor.current_word) or '—'}")
            st.write(f"**Sentence:** {processor.get_sentence() or '—'}")
            st.caption(processor.debug_text or "Hold a hand sign steady to capture a letter.")
    else:
        st.info("Click 'Start' in the video widget to initialize the webcam stream.")


if __name__ == "__main__":
    main()

