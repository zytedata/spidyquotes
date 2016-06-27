FROM scrapinghub/python:3
EXPOSE 5000
WORKDIR /app
CMD ["/app/start-spidyquotes"]
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app
