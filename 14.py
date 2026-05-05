import os, sys, json, wave
from vosk import Model, KaldiRecognizer

wf = wave.open("1.wav", "rb")
model = Model("model1")
rec = KaldiRecognizer(model, wf.getframerate())

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(rec.Result())
print(rec.FinalResult())
