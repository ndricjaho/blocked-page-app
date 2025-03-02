FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app.py
COPY templates templates
COPY static static

# Install gunicorn
RUN pip install gunicorn

# Expose port for gunicorn (adjust if needed - matching docker-compose.yml ports)
EXPOSE 5000

# Command to run Flask app with gunicorn (optimized for typical small app)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "2", "app:app", "--access-logfile", "-"]