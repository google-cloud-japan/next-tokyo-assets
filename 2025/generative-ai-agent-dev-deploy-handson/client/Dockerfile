# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install uv and use it to install dependencies.
RUN pip install uv && uv pip install --system --no-cache -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY webapp.py .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PORT 8080

# Run webapp.py when the container launches
CMD ["streamlit", "run", "webapp.py", "--server.port=8080", "--server.enableCORS=false"]
