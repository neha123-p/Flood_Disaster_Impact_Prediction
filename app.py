import os
from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

# ---------------- LOGIN ----------------
USERNAME = "admin"
PASSWORD = "1234"

# ---------------- LOAD DATASET ----------------
df = pd.read_csv("flood_dataset.csv")

X = df[['Rainfall', 'River_Level', 'Population', 'Area']]

y_people = df['People_Affected']
y_deaths = df['Deaths']
y_agri = df['Agri_Loss']
y_economic = df['Economic_Loss']
y_infra = df['Infra_Damage']

# ---------------- TRAIN MODELS ----------------
m1 = RandomForestRegressor().fit(X, y_people)
m2 = RandomForestRegressor().fit(X, y_deaths)
m3 = RandomForestRegressor().fit(X, y_agri)
m4 = RandomForestRegressor().fit(X, y_economic)
m5 = RandomForestRegressor().fit(X, y_infra)

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    user = request.form['username']
    pwd = request.form['password']
    if user == USERNAME and pwd == PASSWORD:
        return redirect('/disaster')
    else:
        return "❌ Invalid Login"

# ---------------- DISASTER PAGE ----------------
@app.route('/disaster')
def disaster():
    return render_template('disaster.html')

# ---------------- LOCATION PAGE ----------------
@app.route('/location', methods=['POST'])
def location():
    disaster = request.form['disaster']
    return render_template('location.html', disaster=disaster)

@app.route('/input', methods=['POST'])
def input_page():
    state = request.form['state']
    district = request.form['district']
    disaster = request.form['disaster']   # ✅ MUST ADD

    return render_template('input.html',
                           state=state,
                           district=district,
                           disaster=disaster)
    
# ---------------- PREDICTION ----------------
@app.route('/predict', methods=['POST'])
def predict():
    disaster = request.form['disaster']
    pop = float(request.form['pop'])
    area = float(request.form['area'])

    data = None   # ✅ initialize

    # ---------------- FLOOD ----------------
    if disaster == "Flood":
        rain = float(request.form['rain'])
        river = float(request.form['river'])
        data = [[rain, river, pop, area]]

    # ---------------- FIRE ----------------
    elif disaster == "Fire":
        temp = float(request.form['temp'])
        humidity = float(request.form['humidity'])
        wind = float(request.form['wind'])
        data = [[temp, humidity, wind, pop]]

    # ---------------- EARTHQUAKE ----------------
    elif disaster == "Earthquake":
        magnitude = float(request.form['magnitude'])
        depth = float(request.form['depth'])
        data = [[magnitude, depth, pop, area]]

    # ❌ Safety check
    if data is None:
        return "❌ Invalid disaster type"

    # ---------------- PREDICTION ----------------
    people = int(m1.predict(data)[0])
    deaths = int(m2.predict(data)[0])
    agri = round(m3.predict(data)[0], 2)
    economic = round(m4.predict(data)[0], 2)
    infra = round(m5.predict(data)[0], 2)

    # ✅ constraints
    people = min(people, int(pop))
    deaths = min(deaths, people)

    return render_template('result.html',
                           people=people,
                           deaths=deaths,
                           agri=agri,
                           economic=economic,
                           infra=infra)

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)