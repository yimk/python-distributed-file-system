FROM python:3
ADD server.py /


RUN pip install pymongo
RUN pip install flask

CMD [ "python", "./server.py" ]