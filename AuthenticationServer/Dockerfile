FROM python:3
ADD server.py /


RUN pip install pymongo
RUN pip install flask
RUN pip install base64
RUN pip install json
RUN pip install requests

CMD [ "python", "./server.py" ]