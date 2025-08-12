FROM python:3.11.2-slim
EXPOSE 8000
RUN mkdir /usr/local/app
WORKDIR /usr/local/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY main.py map.html ./
CMD ["gunicorn", "main:app", "-w", "2", "--threads", "2", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--worker-class", "uvicorn.workers.UvicornWorker"]
