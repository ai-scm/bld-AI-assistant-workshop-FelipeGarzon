FROM python:3.11-slim-bookworm 

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# default Streamlit port
EXPOSE 8501

# The command to run the app
# --server.address=0.0.0.0 is CRITICAL for Docker networking
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]