from flask import Flask, Response
from prometheus_client import generate_latest, CollectorRegistry, Gauge
import requests
import os 

app = Flask(__name__)

FLOWER_API_URL = os.getenv("URI")
CELERY_TASK_STATE = Gauge('celery_task_state', 'State of Celery tasks', ['state'])

def fetch_flower_metrics():
    response = requests.get(FLOWER_API_URL)
    print(response)
    data = response.json()
    state_counts = {}
    for task_id, task_info in data.items():
        state = task_info['state']
        state_counts[state] = state_counts.get(state, 0) + 1
        
    for state, count in state_counts.items():
        CELERY_TASK_STATE.labels(state).set(count)

@app.route('/metrics')
def metrics():
    registry = CollectorRegistry()
    fetch_flower_metrics()
    return Response(generate_latest(registry), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)