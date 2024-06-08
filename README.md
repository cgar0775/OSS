# Easy Find - Local Service Browsing and Booking System

## Solution to the Challenge Statement

We plan to utilize HTML, CSS, and JavaScript for the frontend development platform for the application interface, alongside a Python-based backend connected to our CISE database server via a series of MySQL commands. We also plan to design this system (both backend and frontend) ahead of time and adapt as we go along.

## Product Vision

Easy Find, presented by CCOM, is designed for both local service-seeking customers and small businesses that may find it difficult or expensive to maintain a personal booking system. Easy Find provides a local service browsing and booking system, eliminating the expense and manpower required to maintain the system while also offering an opportunity for further business outreach and development. By being listed as a service on our platform alongside various other services, Easy Find offers a one-stop shop for any consumer looking for services ranging from massages to handymen. Our user experience and filtering set Easy Find apart from other popular services like Booksy, which can be confusing or difficult to search for exactly what the consumer desires.

## Project Structure

```
my_flask_app/
├── app/
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── script.js
│   │   └── images/
│   ├── (Misc Python Classes)
├── run.py
├── requirements.txt
└── .env
```

### Explanation of Each Component

- **`app/`**: This directory contains the main application package.
  - **`__init__.py`**: Initializes the Flask app.
  - **`routes.py`**: Contains the route definitions for the application.
  - **`templates/`**: Contains HTML templates.
    - **`index.html`**: The main HTML template for the home page.
  - **`static/`**: Contains static files (CSS, JavaScript, images, etc.).
    - **`css/`**: Custom stylesheet.
    - **`js/`**: Custom JavaScript file.
    - **`images/`**: Image files.
  - **`models.py`**: For database models if using an ORM like SQLAlchemy.
  - **`forms.py`**: For form classes if using Flask-WTF.
  - **`utils.py`**: For utility functions or helper functions used throughout the application.
- **`config.py`**: Configuration settings for the application.
- **`run.py`**: Used to run the Flask development server.
- **`requirements.txt`**: Lists the Python dependencies for the project.
- **`.env`**: Contains environment variables (e.g., secret keys, database URIs).

## Setting Up the Project

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd my_flask_app
    ```

2. **Create a virtual environment and activate it:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    Create a `.env` file in the root directory with the following content:
    ```env
    SECRET_KEY=your_secret_key_here
    ```

5. **Run the application:**
    ```sh
    python run.py
    ```

## Using the Application

Navigate to `http://127.0.0.1:5000/` in your web browser to view the application.

## Project Dependencies

- Flask
- Flask-SQLAlchemy (if using SQLAlchemy ORM)
- Flask-WTF (if using forms)
- Flask-Migrate (if handling database migrations)
- Python-Dotenv (for environment variables)

## Contributing

We welcome contributions to improve Easy Find. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch with a descriptive name.
3. Make your changes.
4. Submit a pull request.

## License

This project is licensed under the MIT License.

---

This README provides an overview of the Easy Find project, including its purpose, setup instructions, and usage guidelines. By following this structure, contributors and users can easily understand and get started with the project.