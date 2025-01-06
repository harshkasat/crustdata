# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements to leverage Docker cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port Chainlit runs on
EXPOSE 8000


# Command to start the application with Chainlit
CMD ["chainlit", "run", "my_cl_app.py", "-h", "0.0.0.0", "-p", "8000"]
