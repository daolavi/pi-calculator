import random
import time

def lambda_handler(event, context):
    start = time.time()

    shots = (int)(event["shots"])
    reporting_ratio = (int)(event["reporting_ratio"])
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
    
    return {
      'duration': duration,
      'values': values
    }
