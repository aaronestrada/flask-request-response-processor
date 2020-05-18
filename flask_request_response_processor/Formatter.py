import json
from functools import cached_property

__json_separators__ = (',', ':')


class FlaskRequestFormatter:
    """
    Property formatter for Flask request object
    """

    def __init__(self, request):
        """
        Class constructor
        :param request: Request object to format data
        """
        self.__request__ = request

    @cached_property
    def query_string(self) -> str:
        """
        Query string for current request
        :return: String with query string
        """
        # Query string decoding
        try:
            query_string = self.__request__.query_string.decode('utf-8')
        except UnicodeEncodeError:
            query_string = ''
        return query_string

    @cached_property
    def headers(self) -> dict:
        """
        Dictionary with headers as key -> value
        :return:
        """
        headers = self.__request__.headers.to_wsgi_list()
        return {header[0]: header[1] for header in headers if len(header) == 2}

    @cached_property
    def payload_raw(self) -> str:
        """
        Raw value for payload
        :return: String value for payload
        """
        try:
            payload = self.__request__.get_data().decode('utf-8')
        except UnicodeEncodeError:
            payload = ''
        return payload

    @cached_property
    def payload_json(self) -> dict:
        """
        Attempt to retrieve JSON value for payload. Returns None if no JSON could be found in payload.
        :return:
        """
        # Payload data from request
        return self.__request__.get_json(silent=True)

    @cached_property
    def payload_json_compressed_str(self) -> str:
        """
        Compressed JSON as string for payload
        :return:
        """
        try:
            payload = json.dumps(self.payload_json, separators=__json_separators__)
        except json.JSONDecodeError:
            payload = ''
        return payload

    @cached_property
    def payload_is_json(self) -> bool:
        """
        Validate that payload is of type JSON (using headers)
        :return: Whether the payload is of type JSON or not
        """
        headers_js = self.headers
        return 'Content-Type' in headers_js \
               and headers_js['Content-Type'] == 'application/json' \
               and self.payload_json is not None


class FlaskResponseFormatter:
    """
    Property formatter for Flask response object
    """

    def __init__(self, response):
        """
        Class constructor
        :param response: Response object from Flask to format data
        """
        self.__response__ = response

    @cached_property
    def response_raw(self) -> str:
        """
        Raw response as string
        :return:
        """
        try:
            response_data = self.__response__.get_data(as_text=True)
        except RuntimeError:
            # For files that are not possible to convert as text, a RuntimeError exception is thrown
            response_data = ''

        return response_data

    @cached_property
    def response_json(self) -> dict:
        """
        Attempt to retrieve JSON response
        :return:
        """
        response_data = None

        try:
            response_data = json.loads(self.response_raw)
        except json.JSONDecodeError:
            pass

        return response_data

    @cached_property
    def response_json_compressed_str(self) -> str:
        """
        Retrieve compressed JSON as string for response
        :return:
        """
        try:
            response = json.dumps(self.response_json, separators=__json_separators__)
        except json.JSONDecodeError:
            response = ''
        return response

    @cached_property
    def response_is_json(self) -> bool:
        """
        Validate that response is of type JSON (using headers)
        :return: Whether the response is of type JSON or not
        """
        return self.__response__.content_type == 'application/json' and self.response_json is not None
