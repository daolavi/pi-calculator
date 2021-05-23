from flask import Flask, json, render_template, jsonify
import requests
from concurrent.futures import ProcessPoolExecutor, as_completed
import math
import boto3
import os
from datetime import datetime

os.environ['AWS_SHARED_CREDENTIALS_FILE']='./.aws/credentials'

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/history/getData")
def getHistoryData():
    #f = open("data.txt", "r")
    #data = f.read()
    s3 = boto3.resource('s3')
    content_object = s3.Object('pihistory', 'data.txt')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    print(file_content)
    return jsonify(file_content)

@app.route("/getValues/<service>/<shots>/<resources>/<reporting_ratio>/<digits>")
def run(service, shots, resources, reporting_ratio, digits):
    shots = (int)(shots)
    resources = (int)(resources)
    reporting_ratio = (int)(reporting_ratio)
    digits = (int)(digits)

    loop = 0
    max_loop = 3
    is_matched = False
    time_consuming_in_second = 0 
    while loop < max_loop and not is_matched:
      print(loop)
      with ProcessPoolExecutor(max_workers=60) as executor:
          futures = [executor.submit(get_values, service, (int)(shots/resources), reporting_ratio) for i in range(0, resources)]
          results = []
          counter = 0
          rawData = []
          for future in as_completed(futures):
              counter += 1
              result = future.result()
              time_consuming_in_second += result["duration"]
              values = result["values"]
              rawData.extend(values)
              for record in values:
                obj = {
                  'resource_id': counter,
                  'incircle': record[0],
                  'shots': record[1],
                }
                results.append(obj)

      final_pi = calculate_final_pi(rawData)

      # Lambda $
      priceInSecond = 1 
      if service == 'EC2':
        priceInSecond = 2 

      cost = time_consuming_in_second * priceInSecond
      is_matched = check_pi_value(final_pi, digits)
      loop += 1
    
    #write_data(shots, resources, reporting_ratio, digits, final_pi, cost)
    write_data_to_s3(shots, resources, reporting_ratio, digits, final_pi, cost)

    return {
      'final_pi': final_pi,
      'cost': cost,
      'is_matched': is_matched,
      'data': results
    }

def get_values(service, shots, reporting_ratio):
    url = 'https://fup81ysmfb.execute-api.us-east-1.amazonaws.com/default/pi_calculator?' + 'shots=' + (str)(shots) + '&reporting_ratio=' + (str)(reporting_ratio)
    if (service == "EC2"):
      url = 'http://67.202.13.251:5000/pi_calculator/' + (str)(shots) + '/' + (str)(reporting_ratio)

    reponse = requests.get(url)
    return reponse.json()

def write_data_to_s3(shots, resources, reporting_ratio, digits, final_pi, cost):
    s3 = boto3.resource('s3')
    object = s3.Object('pihistory', 'data.txt')
    content_object = s3.Object('pihistory', 'data.txt')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    now = datetime.utcnow()
    record = (str)(shots) + '\t'  + (str)(resources) + '\t' + (str)(reporting_ratio) + '\t' + (str)(digits) + '\t' + (str)(final_pi) + '\t' +  (str)(cost) + '\t' + (str)(now) + '\n'
    file_content += record
    print(file_content)
    object.put(Body=file_content)

def check_pi_value(pi_value, digits):
    is_matched = False
    pi_value_str = (str)(pi_value)
    if (len(pi_value_str) < (digits + 1)):
      number = digits + 1 - len(pi_value_str)
      for i in range(0, number):
        pi_value_str += '0'

    piStr = (str)(math.pi)[0:(digits+1)]
    if pi_value_str[0:(digits+1)] == piStr:
        is_matched = True

    return is_matched

def calculate_final_pi(rawData):
  incircle = 0
  shots = 0
  for record in rawData:
    incircle += record[0]
    shots += record[1]

  final_pi = 4.0 * incircle / shots
  return final_pi