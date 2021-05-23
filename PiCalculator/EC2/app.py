from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

@app.route('/pi_calculator/<s>/<q>')
def pi_calculator(s, q):
    start = time.time()

    shots = (int)(s)
    reporting_ratio = (int)(q)
    incircle = 0
    counter = 0
    values = []
    for i in range(0, shots):
        counter += 1
        random1 = random.uniform(-1.0, 1.0)
        random2 = random.uniform(-1.0, 1.0)
        if((random1*random1 + random2*random2) < 1):
            incircle += 1

        if (counter == reporting_ratio or i == shots-1):
            values.append([incircle, counter])
            counter = 0
            incircle = 0

    duration = time.time() - start
    
    return jsonify(
      duration= duration,
      values=values
    )
