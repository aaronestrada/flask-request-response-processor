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
