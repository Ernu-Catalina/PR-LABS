# Use Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy dependencies and install them
COPY Lab_2/Task_7/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY Lab_2/Task_7 .

# Expose the application port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
