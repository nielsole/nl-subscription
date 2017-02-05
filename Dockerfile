FROM django:1.9.7-python3
ADD ./nlsub /usr/src/app
RUN mkdir /static
RUN pip install -r /usr/src/app/requirements.txt
RUN cd /usr/src/app
EXPOSE 8000
CMD ./manage.py collectstatic && ./manage.py runserver 0.0.0.0:8000