import requests, logging, os
from time import sleep, time

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s', 
                    handlers=[logging.FileHandler('mylog.log', 'a', 'utf-8')], level = logging.DEBUG)

API_TOKEN = os.getenv("API_TOKEN")
url = 'https://dvmn.org/api/long_polling/'

headers = {"Authorization": API_TOKEN}

timestamp = time()
while True:
  try:
    response = requests.get(url, headers=headers, timeout=130,
                            params = {"timestamp": timestamp})
    json_data = response.json()
    if response.ok and not 'error' in json_data: 
        response = response.json()
        print(response)
    elif response.status_code == 401:
        logging.debug('Authoriztion error')
        response.raise_for_status() 
        logging.debug('Server has responded with:', response)
    elif response.status_code == 404:
        logging.debug('Incorrect address in the request')
        response.raise_for_status() 
    elif response.status_code == 500:
        logging.debug('Something is wrong at the server side')
        response.raise_for_status() 
    else:
        if 'detail' in json_data:
            message = json_data['detail']
            logging.debug('Message in detail: ' + message)
        if 'error' in json_data:
            raise requests.exceptions.HTTPError(json_data['error'])
        response.raise_for_status()
    if response["status"] == "found":
      timestamp = response["last_attempt_timestamp"]
    elif response["status"] == "timeout":
      timestamp = response["timestamp_to_request"]
  except requests.exceptions.ReadTimeout as Err:
    timestamp = time()
    logging.debug(Err)
    sleep(5)
  except requests.exceptions.ConnectionError as Err:
    timestamp = time()
    logging.debug(Err)
    sleep(5)
  except Exception as Err:
    logging.debug(Err)
    break
