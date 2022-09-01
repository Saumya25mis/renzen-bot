FROM python:3.8.3-slim-buster
ENV AP /data/app

ADD . $AP/
WORKDIR $AP

RUN pip3 install --no-cache-dir -r src/requirements.txt

CMD [ "python3", "-m", "src/bot.py" ]
