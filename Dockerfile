FROM python:3.12.1-slim
WORKDIR /data/exe2
COPY . .
RUN apt-get update
RUN apt-get install -y build-essential python-dev-is-python3 git
RUN pip install -U pip setuptools wheel
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "run.py"]