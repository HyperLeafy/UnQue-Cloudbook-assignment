# Assignment Project

## How to Run the Project

### Prerequisites
- Python 3.12 or later.

### Steps

1. **Set up a Virtual Environment** (Optional, but recommended):
   ```bash
   python -m venv venv
   On Ubuntu: source venv/bin/activate  
   On Windows: venv\Scripts\activate
2. **Install dependancies**
   ```bash
    pip install -r requirements.txt
3. **Start the FastAPI Server:**
   ```bash
   uvicorn app.main_app:app --reload
4. **To run the automated TEST:**
   ```bash
   pytest --tb=short --disable-warnings -v
   
