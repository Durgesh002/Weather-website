from crypt import methods
import requests
from unicodedata import name
from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'app.db')
app.config['SECRET_KEY'] = "place your secret key here" 

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=255958e445915f7a46ebd0f332e2f215"
    r = requests.get(url).json()
    return r


@app.route('/')
def index_get():
    cities = City.query.all()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)


        weather = {
        "city":city.name,
        "temperature":r['main']['temp'],
        "description":r['weather'][0]['description'],
        "icon":r['weather'][0]['icon']
        }

    weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')
        
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod']==200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'City does not exists in world'
        else:
            err_msg = 'City already exists in database'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully')
    
    return redirect(url_for('index_get'))

@app.route('/delete/<name>/')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted { city.name }','success')
    return redirect(url_for('index_get'))

if __name__=="__main__":
    app.run(debug=True)
