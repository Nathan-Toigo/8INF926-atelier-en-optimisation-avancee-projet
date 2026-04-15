## How to Run the Application

### Option 1: Using Docker Compose (Recommended)
This method ensures all dependencies and environments are correctly configured.

1.  **Build and start the containers:**
    ```bash
    docker-compose up --build
    ```
2.  **Stop the application:**
    ```bash
    docker-compose down
    ```

### Option 2: Using Python Main File
Ensure you have Python 3.x installed and a virtual environment activated.

1. **Enter app directory:**
   ```bash
    cd app
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```bash
    python main.py
   