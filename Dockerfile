FROM python:3.8-slim-buster
WORKDIR /usr/src/app
COPY . ./
RUN pip install -r requirements.txt
EXPOSE 3000
CMD ["python","blog.py"]
