# Use an official Python runtime as a parent image
# Using a specific version like 3.9 is good for reproducibility
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install git for YahooFinance, which is required for pip to install packages from a git repository.
# We also clean up the apt cache in the same layer to keep the image small.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
# This is done first to leverage Docker's layer caching.
# If requirements.txt doesn't change, this layer won't be re-run on future builds.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Expose the port that Streamlit runs on
EXPOSE 8501

# Define the command to run your app
# Replace 'app.py' with the name of your main Python script
CMD ["streamlit", "run", "app.py"]