# Response processor for Flask applications
This extension integrates an ``after_request`` function for a Flask application to execute a defined function whenever a specific status code from response occurs. The extension is useful in case it is necessary to perform an action whenever a status code occurs (e.g. sending a mail notification for internal server error codes).  

The list of status codes that execute the defined function are specified by the ``REQUEST_RESPONSE_PROCESSOR_STATUS_CODES`` variable (via Flask configuration). If such list is empty, the ``after_request`` function will execute the defined function. 

It is also possible to use the list of status codes that, if occurring, will not execute the desired function. This behavior is set with the flag ``REQUEST_RESPONSE_PROCESSOR_STATUS_CODES_EXCLUDE_ONLY`` (True | False). 

## Requirements
* Python >= 3.8
* Flask

## Installation
Install the extension via *pip*:

```bash
pip install git@github.com/aaronestrada/flask-request-response-processor.git@0.1
```

## Example
The library can be accessed via ``FlaskRequestResponseProcessor`` class. The instance of this object needs to define the ``process_request_response`` behavior function via decorators. The function receives the following parameters: (1) Flask request; (2) Flask response; (3) start/end time for the request. In this function you can verify/process all the available information to pass it to the principal function you are trying to attempt whenever a status code is found (e.g. mail notification, response logging, etc.).

```python
import logging
from datetime import datetime
from flask import Flask, request as flask_request, abort
from flask_request_response_processor import FlaskRequestResponseProcessor, FlaskRequestFormatter, \
    FlaskResponseFormatter

app = Flask(__name__)

# List of status codes to filter
app.config['REQUEST_RESPONSE_PROCESSOR_STATUS_CODES'] = [500, 503]

# If True, all status codes will execute the process function, 
# except those on the REQUEST_RESPONSE_PROCESSOR_STATUS_CODES list.
app.config['REQUEST_RESPONSE_PROCESSOR_STATUS_CODES_EXCLUDE_ONLY'] = False

"""
The FlaskRequestResponseProcessor object needs to define the 'process_request_response' 
function via decorators.

Such function will be executed whenever the status code is on the configuration variable 
'REQUEST_RESPONSE_PROCESSOR_STATUS_CODES' or if such list is empty.

The function receives the request and response objects, plus the start/end time for the 
request. In this function you can verify/process all the available information to pass 
it to the principal function you are trying to attempt whenever a status code is found 
(e.g. mail notification, response logging, etc.).
"""
# Handler for response
response_handler = FlaskRequestResponseProcessor(app=app)


@response_handler.process_request_response
def process_request_response(request: flask_request,
                             request_start_time: datetime,
                             request_end_time: datetime,
                             response):
    """
    Extract available information from request and response
    :param request: flask.request object
    :param request_start_time: UTC start time for request
    :param request_end_time: UTC end time for request
    :param response: Response from processed resource
    :return:
    """
    """
    The extension includes 'FlaskRequestFormatter' and 'FlaskResponseFormatter' 
    classes to retrieve some of the basic information from request and response.
    """
    request_formatter = FlaskRequestFormatter(request=request)
    response_formatter = FlaskResponseFormatter(response=response)

    payload = request_formatter.payload_json_compressed_str \
        if request_formatter.payload_is_json is True \
        else request_formatter.payload_raw

    response_data = response_formatter.response_json_compressed_str \
        if response_formatter.response_is_json \
        else response_formatter.response_raw

    request_time = str(request_end_time - request_start_time)

    # After processing data, you can send mail notifications, logging request, etc.
    logging.error({
        'status_code': response.status_code,
        'path': request.path,
        'payload': payload,
        'date': request_end_time.strftime('%d %B, %Y %H:%M:%S'),
        'time': request_time,
        'method': request.method,
        'response': response_data
    })


@app.route('/error', methods=['get'])
def error():
    abort(503)


@app.route('/ok', methods=['get'])
def ok():
    return 'Ok'


if __name__ == '__main__':
    app.run()
```

Delayed application configuration of ``FlaskRequestResponseProcessor`` is also supported using the ``init_app`` method:

```python
from flask import Flask
from flask_request_response_processor import FlaskRequestResponseProcessor

app = Flask(__name__)
response_handler = FlaskRequestResponseProcessor()
# ...
response_handler.init_app(app=app)
```          

## Testing
To run the example code:
```bash
FLASK_APP=test.py FLASK_DEBUG=1 FLASK_ENV=development flask run
```

Execute the following tests using cURL:

### No execution of ``after_request``
```bash
curl -X GET http://127.0.0.1:5000/ok
```

### Execution of ``after_request``
```bash
curl -X GET http://127.0.0.1:5000/error
```
