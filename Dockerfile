# read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./views /code/views
COPY ./YuanAPI.py /code/YuanAPI.py

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ENV TRANSFORMERS_CACHE /code/.cache

RUN chmod 777 /code/
RUN mkdir /code/.cache
RUN chmod 777 /code/.cache

CMD ["python3", "YuanAPI.py"]
