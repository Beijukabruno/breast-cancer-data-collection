FROM python:3.9

WORKDIR /code

# Copy requirements and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application files
COPY ./app.py /code/
COPY ./districts.txt /code/
COPY ./README.md /code/

# Create data directory
RUN mkdir -p /code/data

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]