from flask import Flask, render_template, request
import requests
import json
import datetime
import calendar
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os

app = Flask(__name__)

@app.route("/")
def hello():
    leaflet = os.getenv('LEAFLET_API_KEY')
    return render_template("index.html", leaflet=leaflet)

@app.route('/predict', methods=['GET','POST'])
def predict():
    # values = request.get_json()
    # print(values)
    request.form = request.form.to_dict()
    print(request.form['Origin'])
    print(request.form['Destination'])
    print('done')
    #TODO currently the form is not grabbing the values because it is an ajax called so it doesn't have a form value
    #origin = request.form.get("Origin")
    origin = request.form['Origin']
    
    #origin = request.form['origin']
    origin = str(origin)
    origin = origin.replace(" ", "")
    #destination = request.form.get("Destination")
    destination = request.form['Destination']
    
    #destination = request.form['destination']
    destination = str(destination)
    destination = destination.replace(" ", "")
    print('start: ' + origin)
    print('end: ' + destination)
    #TODO check if form has been filled properly
    google_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins='
    google_url += origin
    google_url += '&destinations='
    google_url += destination
    api = os.getenv('GOOGLE_API_KEY')
    google_url += '&key='
    google_url += api

    #resp = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=40.6655101,-73.89188969999998&destinations=40.6905615,-73.9976592&key=app_key')
    resp = requests.get(google_url)
    if resp.status_code != 200:
    # This means something went wrong.
        raise ApiError('GET /tasks/ {}'.format(resp.status_code))
    print(resp.json())
    json_resp = resp.json()
    print(json_resp)
    destination_resp = json_resp['destination_addresses'][0]
    print(destination_resp)
    origin_resp = json_resp['origin_addresses'][0]
    distance = json_resp['rows'][0]['elements'][0]['distance']['text']
    distance = distance.replace(" mi", "")
    print(distance)
    duration = json_resp['rows'][0]['elements'][0]['duration']['value']
    print(duration)
    today = datetime.datetime.today()
    weekday = calendar.day_name[today.weekday()]
    month = calendar.month_name[today.month]
    time = datetime.datetime.now()
    current_time = time.strftime("%H")
    current_time = int(current_time)
    print(current_time)
    if current_time > 5:
        hour_cat = "early_morning"

    elif current_time > 9:
        hour_cat = "morning_rush"
    elif current_time > 16:
        hour_cat = "midday"
    elif current_time > 19:
        hour_cat = "evening_rush"
    else:
        hour_cat = "night"

    print(duration)
    print(distance)
    print(weekday)
    print(month)
    print(hour_cat)
    url = 'https://ussouthcentral.services.azureml.net/workspaces/ae1b51b0047b4808a1e51dfab0763392/services/fc54988091024a11b9c3303b066dc090/execute?api-version=2.0&details=true'
    api_key = os.getenv('AZURE_API_KEY')
    data =  {

        "Inputs": {

                "input1":
                {
                    "ColumnNames": ["trip_seconds", "trip_miles", "fare", "day", "month", "hour_cat"],
                    "Values": [ [ duration, distance, "0", weekday, month, hour_cat ] ]
                },        
        },
        "GlobalParameters": {
        }
    }
    #data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.json()['Results']['output1']['value']['Values'][0][0])
    fare = r.json()['Results']['output1']['value']['Values'][0][0]

    resp_array = {'fare':fare, 'duration':str(duration), 'distance':str(distance)}
    #return fare
    return resp_array

    #return render_template("index.html", fare=fare)

if __name__ == "__main__":
    app.run()