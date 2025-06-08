# POC - Pedro Management Service
## Getting Started

Follow these steps to set up and run the project locally:

### Prerequisites
- Python 3.8 or higher installed on your system.

### Setup Instructions

1. **Create a Virtual Environment**  
    Run the following command to create a virtual environment:
    ```bash
    python -m venv .venv
    ```

2. **Activate the Virtual Environment**  
    - On Windows:
      ```bash
      .venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

3. **Install Dependencies**  
    Install the required dependencies from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables**  
    Locate the `.env.template` file in the project directory. Rename it to `.env` and fill in the required values as specified in the template. This file contains sensitive configuration details such as API keys or database credentials.

5. **Run the Backend**  
    Use FastAPI to start the backend server locally:
    ```bash
    uvicorn app.main:app --reload
    ```

### Accessing the Application
Once the server is running, you can access the API documentation at:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)