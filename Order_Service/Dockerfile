FROM python:3.9

WORKDIR /app

# Copy everything, including the static folder
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "oService.py"]