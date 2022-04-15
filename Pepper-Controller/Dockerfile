FROM python:2

WORKDIR /usr/src/app

RUN apt update && apt install -y python-tk
RUN apt install telnet
RUN pip install opencv-python==4.2.0.32
COPY . .



COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:./pynaoqi/lib/python2.7/site-packages"


#CMD [ "export", "PYTHONPATH=${PYTHONPATH}:./pynaoqi/lib/python2.7/site-packages" ]
CMD [ "python", "./peppergui.py" ]

#CMD [ "ping", "192.168.2.3" ]
#CMD [ "telnet", "192.168.2.3","9559" ]

