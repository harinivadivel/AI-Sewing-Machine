from flask import Flask, render_template, jsonify
import serial
import threading
import time
import re
import joblib
import numpy as np

app = Flask(__name__)

# AI model
model = joblib.load("model.pkl")

# SERIAL
try:
    ser = serial.Serial('COM9',9600,timeout=1)
    print("Serial Connected")
except:
    ser = None
    print("Serial Not Connected")


latest_data = {
"value":0,
"type":"None",
"dress":[]
}


def read_serial():

    global latest_data

    while True:

        if ser and ser.in_waiting:

            raw = ser.readline().decode(errors="ignore")

            print("RAW:",raw)

            numbers = re.findall(r'\d+',raw)

            for num in numbers:

                value = int(num)

                print("VALUE:",value)

                pred = model.predict(np.array([[value]]))[0]

                print("PRED:",pred)

                latest_data["value"]=value

                if pred==1:

                    latest_data["type"]="Human"

                    latest_data["dress"]=[
                    "Shirt","T-Shirt","Jacket","Hoodie","Blazer"
                    ]

                    ser.write(b'1')

                elif pred==0:

                    latest_data["type"]="Animal"

                    latest_data["dress"]=[
                    "Pet Jacket","Pet Sweater","Pet Raincoat"
                    ]

                    ser.write(b'0')

                else:

                    latest_data["type"]="Unknown"

                    latest_data["dress"]=[
                    "No Suggestion"
                    ]

                    ser.write(b'3')

                print("UPDATED DATA:",latest_data)

        time.sleep(0.2)


thread = threading.Thread(target=read_serial)
thread.daemon=True
thread.start()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/data")
def data():

    return jsonify(latest_data)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)