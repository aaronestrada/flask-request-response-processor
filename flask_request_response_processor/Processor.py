import logging
from datetime import datetime
from flask import Flask, request as flask_request, g


class FlaskRequestResponseProcessor:
    """
    This class will handle after_request for the application to process the information from
    request + response whenever a status code from response occurs.

    To set the list of filtered status codes, you need to specify the variable
    REQUEST_RESPONSE_PROCESSOR_STATUS_CODES via the Flask configuration variables.

    The instance of this class must specify the following function with decorators:

    process_request_response(request: flask.request, response, request_start_date, request_end_date)
    ------------------------------------------------------------------------------------------------
    The method receives the request and the response as input, and it is responsible of processing
    executing defined functions by using data from request and response.
    """

    # Decorator functions
    __process_request_response_f__ = None

    def __init__(self, app: Flask = None, prefix: str = 'REQUEST_RESPONSE_PROCESSOR'):
        """
        Class constructor
        :param app: Flask application to configure
        :param prefix: Prefix to use for environment variables to use
        """
        prefix = prefix.strip()
        if prefix == '':
            prefix = 'REQUEST_RESPONSE_PROCESSOR'

        self.__label_status_codes__ = f'{prefix}_STATUS_CODES'

        # Label to retrieve boolean flag to filter everything except the status code in list.
        # If True, all the status codes will execute the '__process_request_response_f__' function,
        # exception the status codes in the list.
        self.__label_status_codes_exclude_only_ = f'{prefix}_STATUS_CODES_EXCLUDE_ONLY'

        if app is not None:
            self.init_app(app=app)

    # ----------
    # Decorators
    # ----------
    def process_request_response(self, f):
        """
        Decorator to set function that extracts information from request and response.
        The function returns a dictionary with necessary information to send to the
        function __message_attempt_f__.

        :param f: Function to set as abort function
        :return:
        """
        self.__process_request_response_f__ = f

    # ----------------
    # Public functions
    # ----------------
    def init_app(self, app: Flask):
        """
        Initialize application with logging configuration
        :param app: Flask application to configure
        :return:
        """
        filter_status_codes = app.config.get(self.__label_status_codes__)

        if type(filter_status_codes) != list:
            filter_status_codes = []

        filter_status_codes_exclude_only = app.config.get(self.__label_status_codes_exclude_only_)
        if type(filter_status_codes_exclude_only) != bool:
            filter_status_codes_exclude_only: bool = False

        filter_status_codes_empty = len(filter_status_codes) == 0

        @app.before_request
        def before_request():
            """
            Processing before accepting request
            :return:
            """
            # Keep UTC time instead of local time
            g.frr_start_time = datetime.utcnow()

        @app.after_request
        def after_request(response):
            """
            Logging after processing request
            :param response: Response from request
            :return: Response to output to user
            """
            end_time = datetime.utcnow()

            """
            Inside the decorated function __process_request_response_f__ it will be possible to 
            process needed data to return a dictionary object.                                                
            
            Execute defined function whenever:            
            1) List of status codes is empty
            2) Status code is in list and exclusion flag is False
            3) Status code not is in list and exclusion flag is True
            """
            process_func = True if filter_status_codes_empty is True \
                else (response.status_code in filter_status_codes) != filter_status_codes_exclude_only

            if process_func is True:
                try:
                    # Status code in filtered list, create mail object
                    if self.__process_request_response_f__ is not None:
                        self.__process_request_response_f__(
                            request=flask_request,
                            response=response,
                            request_start_time=g.frr_start_time,
                            request_end_time=end_time
                        )
                except BaseException as error:
                    # Response must be sent even if there is an error
                    logging.error('An execution error occurred on decorator function on after_request; skipping.',
                                  error)

            return response
