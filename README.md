# Skål

Skål is a FastAPI application designed to manage and interact with various functionalities related to brewing, including recipes, ABV% calculations, and more. This project aims to provide a comprehensive, but simple, web application for brewers to manage their brewing processes.

## Features

- **SQLite Database Interaction**: Add, edit, and view data stored in an SQLite database.
- **ABV% Calculation**: Calculate the Alcohol By Volume percentage and estimate calories based on user input.
- **Database Maintenance**: Includes commands for backing up and importing the database.

## Installation

To get started with Skål, follow these steps:
### Using Virtual Environment

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/daytonjones/Skal.git
    cd Skal
    ```

2. **Set Up a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Application**:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --ssl-keyfile key.pem --ssl-certfile cert.pem
    ```
    Open https://127.0.0.1:8080 in your web browser. Default User/Pass is "admin/password123" and you will be prompted to create a user at first login.


### Using Docker

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/daytonjones/Skal.git
    cd Skal
    ```

2. **Build the Docker Image**:
    ```bash
    docker build -t skal-app .
    ```

3. **Run the Docker Container**:
    ```bash
    docker run -d -p 8080:8080 skal-app
    ```
    Open https://127.0.0.1:8080 in your web browser. Default User/Pass is "admin/password123" and you will be prompted to create a user at first login.

## Configuration

The application uses an SQLite database which will be created at the first time the app is started.  To access the TiltPi data (if using a Tilt with TiltPi) just follow the instructions in the app to link to your shared reports.

## Usage

- **Accessing the Application**: Navigate to the application's URL in your web browser.
- **Viewing Recipes**: Access and manage brewing recipes.
- **Calculating ABV%**: Use the provided form to calculate the ABV% and estimated calories for your brews.

## Contributing

If you'd like to contribute to the project, please fork the repository and submit a pull request with your changes. Ensure that you follow the project's coding guidelines and include relevant tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or feedback, please contact me.

### Demo

[https://skaldemo.gecko.org](https://skaldemo.gecko.org)
**User**: demo
**Password**: password123
