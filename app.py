from flask import Flask, render_template, jsonify
import serial
import threading
import time
import re
import joblib
import numpy as np

app = Flask(__name__)

# ---------------- LOAD MODEL ----------------

model = joblib.load("model.pkl")
print("AI Model Loaded")

# ---------------- SERIAL ----------------

try:
    ser = serial.Serial('COM5',9600,timeout=1)
    print("Serial Connected")
except:
    print("Serial Not Available")
    ser = None


latest_data = {
    "value":0,
    "type":"None",
    "dress":"None"
}


# ---------------- SERIAL READ ----------------

def read_serial():

    global latest_data

    while True:

        if ser:

            raw = ser.read(50).decode(errors="ignore")

            if raw:

                print("RAW:",raw)

                numbers = re.findall(r'\d+',raw)

                for num in numbers:

                    value = int(num)

                    print("VALUE:",value)

                    # ---------------- AI PREDICTION ----------------

                    pred = model.predict(np.array([[value]]))[0]

                    print("PRED:",pred)

                    latest_data["value"] = value

                    # 1 = HUMAN
                    if pred == 1:

                        latest_data["type"] = "Human"
                        latest_data["dress"] = "Shirt, Jacket, T-Shirt"

                        if ser:
                            ser.write(b'1')

                    # 0 = ANIMAL
                    elif pred == 0:

                        latest_data["type"] = "Animal"
                        latest_data["dress"] = "Animal Safety Cover"

                        if ser:
                            ser.write(b'0')

                    # 2 → UNKNOWN
                    else:

                        latest_data["type"] = "Unknown"
                        latest_data["dress"] = "No Suggestion"

                        if ser:
                            ser.write(b'3')

        time.sleep(0.3)


thread = threading.Thread(target=read_serial)
thread.daemon = True
thread.start()


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/data")
def data():
    return jsonify(latest_data)


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)