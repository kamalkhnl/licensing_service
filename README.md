# Licensing Service

## Introduction

This repository contains a licensing service developed as a side project while working at Paracosma. The service includes an admin panel for generating serial keys and a user interface for assigning and checking the validity of these keys.

## Features

- Admin panel for generating 16-digit serial keys
- User interface for assigning serial keys to devices
- Check the validity of serial keys
- Track the usage and activation of serial keys

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/kamalkhnl/licensing_service.git
    cd licensing_service
    ```

2. Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Apply the migrations:
    ```bash
    python manage.py migrate
    ```

5. Create a superuser for the admin panel:
    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

### Admin Panel

1. Access the admin panel at `http://127.0.0.1:8000/admin/`.
2. Log in with the superuser credentials.
3. Generate serial keys using the "Serial Keys" section.

### API Endpoints

- **Assign Key**: `POST /keys/assign_key/`
    - Request body:
        ```json
        {
            "key": "YOUR_SERIAL_KEY",
            "device_id": "YOUR_DEVICE_ID"
        }
        ```
    - Response:
        ```json
        {
            "status": "success",
            "message": "Key activated"
        }
        ```

- **Check Key**: `POST /keys/check_key/`
    - Request body:
        ```json
        {
            "key": "YOUR_SERIAL_KEY",
            "device_id": "YOUR_DEVICE_ID"
        }
        ```
    - Response:
        ```json
        {
            "status": "success",
            "message": "Key activated"
        }
        ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
