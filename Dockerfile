FROM django:1.9.7-python3
ADD ./nlsub /usr/src/app
RUN mkdir /static
RUN pip install -r /usr/src/app/requirements.txt
WORKDIR /usr/src/app
EXPOSE 8000
CMD ./manage.py collectstatic --noinput && gunicorn -w 4 -b 0.0.0.0:8000 nlsub.wsgi:application