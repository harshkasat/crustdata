# Use an official Python runtime as the base image
FROM python:3.9-slim

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
ENV PINECONE_API_KEY=<your-pinecone-api-key>
ENV GROQ_API_KEY=<your-groq-api-key>

# Expose the port Chainlit runs on
EXPOSE 8000

# Preload the HuggingFace model to avoid reloading
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')"

# Command to start the application with Chainlit
CMD ["chainlit", "run", "my_cl_app.py", "-h", "0.0.0.0", "-p", "8000"]
