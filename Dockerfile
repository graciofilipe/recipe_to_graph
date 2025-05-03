# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by the application (e.g., graphviz)
# Run as root before potentially switching user
RUN apt-get update && \
    apt-get install -y graphviz --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy the dependencies file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Disables the cache to keep the image size smaller
# --upgrade pip: Ensure pip is up to date
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the working directory
COPY . /app

# Make port 8080 available to the world outside this container (as expected by Cloud Run)
EXPOSE 8080

# Define environment variables (if needed, e.g., PROJECT_ID could be set here or at runtime)
# ENV GOOGLE_APPLICATION_CREDENTIALS=/path/to/keyfile.json # Example if using service account keys
# ENV PORT=8080 # Cloud Run sets this automatically, but can be explicit

# Run the Streamlit application when the container launches
# Use the port specified by Cloud Run (or default 8080)
# Disable CORS and XSRF protection as per instructions (consider security implications)
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
