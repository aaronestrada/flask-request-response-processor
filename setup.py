from distutils.core import setup

setup(
    name='flask-request-response-processor',
    version='0.1',
    description='Extension handling after_request function for a Flask application whenever a specific status code from response occurs.',
    license='BSD',
    author='Aaron Estrada Poggio',
    author_email='aaron.estrada.poggio@gmail.com',
    url='https://github.com/aaronestrada/flask-request-response-processor',
    packages=['flask_request_response_processor'],
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'Flask>=1.1.0'
    ]
)
