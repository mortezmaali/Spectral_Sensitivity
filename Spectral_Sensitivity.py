# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 21:22:58 2024

@author: Morteza
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# Function to convert wavelength to sRGB
def wavelength_to_rgb(wavelength):
    gamma = 0.8
    intensity_max = 1.0
    factor = 0.0
    R = G = B = 0.0

    if 380 <= wavelength < 440:
        R = (440 - wavelength) / (440 - 380)
        G = 0.0
        B = 1.0
    elif 440 <= wavelength < 490:
        R = 0.0
        G = (wavelength - 440) / (490 - 440)
        B = 1.0
    elif 490 <= wavelength < 510:
        R = 0.0
        G = 1.0
        B = (510 - wavelength) / (510 - 490)
    elif 510 <= wavelength < 580:
        R = (wavelength - 510) / (580 - 510)
        G = 1.0
        B = 0.0
    elif 580 <= wavelength < 645:
        R = 1.0
        G = (645 - wavelength) / (645 - 580)
        B = 0.0
    elif 645 <= wavelength <= 780:
        R = 1.0
        G = 0.0
        B = 0.0

 # Adjust intensity
    factor = 1
    R = (R * factor) ** gamma
    G = (G * factor) ** gamma
    B = (B * factor) ** gamma

    return int(R * 255), int(G * 255), int(B * 255)

# Function to draw the luminous efficiency function
def draw_luminous_efficiency():
    wavelengths = np.arange(380, 781, 1)
    v_lambda = np.exp(-0.5 * ((wavelengths - 555) / 80) ** 2)

    fig = Figure(figsize=(10, 5))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.plot(wavelengths, v_lambda, color='green', linewidth=2)
    ax.set_title("Luminous Efficiency Function (Standard Observer)", fontsize=16)
    ax.set_xlabel("Wavelength (nm)", fontsize=12)
    ax.set_ylabel("Relative Sensitivity", fontsize=12)
    ax.grid(True)

    canvas.draw()
    img = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
    img = img.reshape(canvas.get_width_height()[::-1] + (3,))
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

# Video parameters
fps = 30
seconds_per_wavelength = 5
width, height = 1920, 1080  # Adjust to fit your laptop screen

# Create a video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video = cv2.VideoWriter("spectrum_video.mp4", fourcc, fps, (width, height))

# Add the luminous efficiency function at the start
luminous_frame = draw_luminous_efficiency()
resized_luminous_frame = cv2.resize(luminous_frame, (width, height))
for _ in range(fps * 5):
    video.write(resized_luminous_frame)

# Add the question prompt
question_text = "Which wavelength do you think\nhumans are more sensitive to?"
frame = np.zeros((height, width, 3), dtype=np.uint8)

# Add question text (split into two lines, with larger font size)
lines = question_text.split("\n")
font_scale = 2.5
thickness = 5
y_offset = height // 3

for i, line in enumerate(lines):
    text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = (width - text_size[0]) // 2
    text_y = y_offset + i * (text_size[1] + 40)
    cv2.putText(frame, line, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

for _ in range(fps * 5):
    video.write(frame)

# Reverse the order of wavelengths
wavelengths = list(range(400, 701, 50))[::-1]

# Create video for each wavelength
wavelengthn = 350
for wavelength in wavelengths:
    color = wavelength_to_rgb(wavelength)
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = color

    # Add wavelength text
    font_scale = 3
    thickness = 5
    wavelengthn = wavelengthn + 50
    text = f"Wavelength: {wavelengthn} nm"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2

    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

    # Write frames for this wavelength
    for _ in range(fps * seconds_per_wavelength):
        video.write(frame)

# Release video writer
video.release()

# Play the video
cap = cv2.VideoCapture("spectrum_video.mp4")
cv2.namedWindow("Spectrum Video", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Spectrum Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Spectrum Video", frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
