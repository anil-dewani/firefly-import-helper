# Firefly III Import Helper

This tool is an extended utility to properly format and trim out un-necessary details from the default exported e-statements of popular banks. The tool parses the e-statements and converts them into Firefly III compatible transactions and uploads each transaction on the firefly III server via its personal access token. If access token is not available, it lets users download the files so they can manually import them to firefly III using the default importer module.

Features:

- Support for all major indian banks (Axis, SBI, ICICI for now)
- Support to parse and import Credit card e-statement PDF files
- Maintain backend database of all amazon orders and sync's it with imported transaction data automatically
- Automatically inserts category of transaction by analyzing common patterns in description texts
- Sends email alerts with detailed report of each parse and import request

Technologies used:
- Django (backend)
- Celery Queue
- Docker
- Selenoid (to parse amazon links)
- Pre-commit


Upcoming features:
- Universal parser to extract transactions from any format of e-statement from any bank worldwide
