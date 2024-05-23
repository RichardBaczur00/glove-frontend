import requests


def create_session(prompt, user_id):
    url = "http://85.120.206.70:80/api/v1/session"
    data = {
        'text': prompt,
        'user_id': 1
    }

    response = requests.post(url, json=data)

    if response.status_code != 200:
        print('Error creating session!')
    
    return response


def put_result_data(session_id, order_number, sensor_data):
    url = f"http://85.120.206.70:80/api/v1/entry/{session_id}"
    data = {
        'session': {
            'text': 'hidden',
            'user_id': 0
        },
        'order_number': order_number,
        'data': sensor_data
    }

    response = requests.post(url, json=data)

    if response.status_code != 200:
        print(response)
        print('Error sending the result to server')
    
    return response
