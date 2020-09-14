FROM python:3.8

WORKDIR /code

RUN pip install pipenv
COPY Pipfile* /code/
RUN cd /code && pipenv lock --requirements > requirements.txt

RUN pip install -r requirements.txt

COPY src/ .

CMD [ "python", "./main.py" ]