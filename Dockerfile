# read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./static /code/static
COPY ./NewYuan.py /code/NewYuan.py

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ENV TRANSFORMERS_CACHE /code/.cache

RUN chmod 777 /code/
RUN mkdir /code/.cache
RUN chmod 777 /code/.cache
RUN cd /code/
CMD ["uvicorn", "NewYuan:app", "--host", "0.0.0.0", "--port", "7860"]
