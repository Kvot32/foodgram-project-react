FROM python:3.9-slim
WORKDIR /app
COPY foodgram/requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install python-dotenv
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["bash", "runserver.sh"]

#CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000", "--chdir", "foodgram"]