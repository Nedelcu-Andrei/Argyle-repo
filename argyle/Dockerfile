FROM python:3.8

RUN pip install -r requirements.txt

WORKDIR ./argyle/

COPY main.py ./argyle/main.py

CMD ["python", "main.py"]