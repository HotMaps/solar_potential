
### Application Structure

.
├── cm
│   ├── app
│   │   ├── api_v1
│   │   │   ├── calculation_module.py
│   │   │   ├── errors.py
│   │   │   ├── __init__.py
│   │   │   └── transactions.py
│   │   ├── constant.py
│   │   ├── decorators
│   │   │   ├── caching.py
│   │   │   ├── __init__.py
│   │   │   ├── json.py
│   │   │   ├── paginate.py
│   │   │   └── rate_limit.py
│   │   ├── exceptions.py
│   │   ├── __init__.py
│   │   ├── logging.conf
│   │   └── utils.py
│   ├── config
│   │   ├── development.py
│   │   ├── __init__.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── Dockerfile
│   ├── gunicorn-config.py
│   ├── requirements.txt
│   ├── run.py
│   ├── test.py
│   └── tests
│       ├── __init__.py
│       ├── test_client.py
│       └── tests.py
├── config
│   ├── development.py
│   ├── __init__.py
│   ├── production.py
│   └── testing.py
├── LICENSE
└── README.md


* `cm/requirements.txt` - The list of Python (PyPi) requirements.
* `app/constant.py` - The `SIGNATURE` variable describe all the parameters of the calculation modules that the main API will need to work properly.
* `app/__init__.py` - Launche the entire application.
* `app/api_v1/transaction.py` - The entrypoint of the registration of the CM to the main webservice. This is the first action that the application is doing 
* `app/docorators/caching.py` - Define decorators for caching the results
* `app/docorators/json.py` - Define decorators to transform dictionary to json
* `app/docorators/paginate` - Define decorators to split the content in several pages
* `app/docorators/rate_limit.py` - Define decorators to respect a certain number or requests, disabled if `DEBUG` variable is True

