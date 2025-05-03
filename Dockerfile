# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

COPY r2g_app ./r2g_app
COPY st_app.py .

# Copy the dependencies file first to leverage Docker cache
COPY r2g_app/requirements.txt .



# Install system dependencies required by the application (e.g., graphviz)
# Run as root before potentially switching user
RUN apt-get update && \
    apt-get install -y graphviz --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*


# Install Python dependencies
# --no-cache-dir: Disables the cache to keep the image size smaller
# --upgrade pip: Ensure pip is up to date
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Optional: Set PYTHONPATH if your simulation code uses relative imports across modules
ENV PYTHONPATH=/app

# Run streamlit_app.py when the container launches
# Use shell form to allow $PORT substitution
ENTRYPOINT streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
