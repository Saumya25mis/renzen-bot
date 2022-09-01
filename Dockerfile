FROM ubuntu
ENV AP /data/app

WORKDIR /src
ADD src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
WORKDIR $AP
CMD [ "python3", "-m", "bot.py" ]
