# Easy Find - Local Service Browsing and Booking System

## Solution to the Challenge Statement

We plan to utilize HTML, CSS, and JavaScript for the frontend development platform for the application interface, alongside a Python-based backend connected to our CISE database server via a series of MySQL commands. We also plan to design this system (both backend and frontend) ahead of time and adapt as we go along.

## Product Vision

Easy Find, presented by CCOM, is designed for both local service-seeking customers and small businesses that may find it difficult or expensive to maintain a personal booking system. Easy Find provides a local service browsing and booking system, eliminating the expense and manpower required to maintain the system while also offering an opportunity for further business outreach and development. By being listed as a service on our platform alongside various other services, Easy Find offers a one-stop shop for any consumer looking for services ranging from massages to handymen. Our user experience and filtering set Easy Find apart from other popular services like Booksy, which can be confusing or difficult to search for exactly what the consumer desires.

## Setting Up the Project

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd oss
    ```

**WINDOWS**

2. Install the Ubuntu emulator from the windows store

3. Install Redis to the Ubuntu emulator

    ```sh
    sudo apt get update
    sudo apt install redis-server
    ```
4. Run the Redis server

   ```sh
   sudo service redis-server start
   ```
   test that redis is active
   ```sh
   redis-cli ping
   ```
   it should respond with PONG

5. Install Oracle
   
   Navigate to https://www.oracle.com/database/technologies/instant-client.html and install Oracle client

   Add Oracle client path as a system variable within environment variables.
   (the system environment variables not user)
   
   Important: Name this system variable ORACLE_HOME.
   
   System->About->Advanced system settings->Environment Variables->Add New in System Variables

**MAC**

2. Install Homebrew
   ```sh
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install Redis
   ```sh
   brew install redis
   ```
4. Start Redis
   ```sh
   brew services start redis
   ```
5. Verify redis
  ```sh
redis-cli ping```
It should respond with PONG

6. Install Oracle
Navigate to https://www.oracle.com/database/technologies/instant-client/macos-intel-x86-downloads.html and download the latest version of instantclient-basic-macos.x64-##.#.#.#.#.zip and instantclient-sqlplus-macos.x64-##.#.#.#.#.zip

Add the path location of the folder containing instantclient in your .env
	    ORACLE_HOME = /users/name/”location”/instantclient_##


7. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

8. **Run the application:**
    ```sh
    python run.py
    ```

## Using the Application

Navigate to `http://127.0.0.1:5000/` in your web browser to view the application.

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
