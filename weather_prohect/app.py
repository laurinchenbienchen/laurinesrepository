from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_text = None
    error_message = None
    if request.method == 'POST':
        city = request.form['city']
        weather_data, error_message = get_weather(city)
        if weather_data:
            weather_text = generate_weather_text(weather_data)
    return render_template('index.html', weather_text=weather_text, error_message=error_message)


def get_weather(city):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return None, data.get('message', 'Error fetching weather data')

    if 'weather' not in data or 'main' not in data:
        return None, 'Invalid response from weather API'

    return data, None


def generate_weather_text(weather_data):
    description = weather_data['weather'][0]['description']
    temperature = weather_data['main']['temp']
    city = weather_data['name']
    country = weather_data['sys']['country']

    text = f"Das aktuelle Wetter in {city}, {country} ist {description} mit einer Temperatur von {temperature}°C."
    return text


if __name__ == '__main__':
    app.run(debug=True)
