Skål

Skål is a FastAPI application designed to manage and interact with various functionalities related to brewing, including recipes, ABV% calculations, and more. This project aims to provide a comprehensive, but simple, web application for brewers to manage their brewing processes.

Features:
- Interaction with an SQLite database for data management.
- ABV% calculation and calorie estimation.
- Database maintenance for database backup and import.

Installation:
To set up Skål, you have two options:

Using Virtual Environment:
1. Clone the repository:
   `git clone https://github.com/daytonjones/Skal.git && cd Skal`

2. Set up a virtual environment:
   `python -m venv venv
   source venv/bin/activate`  # Use `venv\Scripts\activate` on Windows

3. Install dependencies:
   `pip install -r requirements.txt`

4. Run the application:
    `uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --ssl-keyfile key.pem --ssl-certfile cert.pem`
    Open https://127.0.0.1:8080 in your web browser. Default User/Pass is "admin/password123" and you will be prompted to create a user at first login.


Using Docker:
1. Clone the repository:
   `git clone https://github.com/daytonjones/Skal.git && cd Skal`

2. Build the Docker image:
   `docker build -t skal-app .`

3. Run the Docker container:
   `docker run -d -p 8080:8080 skal-app`
   Open https://127.0.0.1:8080 in your web browser. Default User/Pass is "admin/password123" and you will be prompted to create a user at first login.

Configuration:
- The application uses an SQLite database which will be created at the first time the app is started.  To access the TiltPi data (if using a Tilt with TiltPi) just follow the instructions in the app to link to your shared reports.

Usage:
- Navigate to the application's URL to access and manage recipes and other features.

Contributing:
- Fork the repository and submit a pull request with your changes. Follow the coding guidelines and include tests.

License:
- This project is licensed under the MIT License. See the LICENSE file for details.

Contact:
- For questions or feedback, please contact me.
