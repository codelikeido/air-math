import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import pyttsx3
import speech_recognition as sr
import threading
import time

# -------------------------
# TEXT TO SPEECH
# -------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# -------------------------
# VOICE RECOGNITION
# -------------------------
recognizer = sr.Recognizer()

def listen_command():
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=3)
            command = recognizer.recognize_google(audio)
            return command.lower()
        except:
            return ""

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="AirMath Accessibility Mode")
st.title("AirMath - Assistive Audio Mode")

start = st.checkbox("Start System")

if "expression" not in st.session_state:
    st.session_state.expression = ""

if "canvas" not in st.session_state:
    st.session_state.canvas = np.zeros((480,640,3),dtype=np.uint8)

# -------------------------
# MediaPipe Setup
# -------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

def structure_speak(symbol):
    mapping = {
        "+": "plus",
        "-": "minus",
        "*": "multiplied by",
        "/": "divided by"
    }
    return mapping.get(symbol, symbol)

# -------------------------
# SMART ASSIST
# -------------------------
def smart_assist():
    exp = st.session_state.expression

    if exp == "":
        speak("Please start writing your expression.")
        return

    if exp[-1] in "+-*/":
        speak("Please enter the next number.")
        return

    try:
        result = eval(exp)
        speak(f"{read_expression(exp)} equals {result}")
    except:
        speak("Invalid mathematical expression. Please rewrite.")

def read_expression(exp):
    spoken = ""
    for char in exp:
        spoken += structure_speak(char) + " "
    return spoken

# -------------------------
# CAMERA LOOP
# -------------------------
if start:
    cap = cv2.VideoCapture(0)

    speak("Air Math accessibility mode activated.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame,1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        # Placeholder recognition
        # Replace this with CNN prediction
        predicted_digit = None

        if result.multi_hand_landmarks:
            # Here you add digit recognition logic
            pass

        command = listen_command()

        if "clear" in command:
            st.session_state.expression = ""
            speak("Expression cleared")

        elif "solve" in command or "confirm" in command:
            smart_assist()

        elif "repeat" in command:
            speak(read_expression(st.session_state.expression))

        st.write("Current Expression:", st.session_state.expression)

    cap.release()