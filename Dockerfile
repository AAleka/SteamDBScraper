FROM python:3.9.1

WORKDIR /steam_scrape

COPY requirements.txt .

COPY . .

RUN apt update
RUN apt upgrade -y

RUN pip install -r requirements.txt

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install ./google-chrome-stable_current_amd64.deb -y
RUN rm ./google-chrome-stable_current_amd64.deb

RUN mkdir files
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/115.0.5790.170/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip
RUN cp chromedriver-linux64/chromedriver /usr/bin/chromedriver
RUN rm -rf chromedriver-linux64.zip
RUN rm -rf chromedriver-linux64

RUN chmod +x ./main.py

ENTRYPOINT ["./main.py"]
