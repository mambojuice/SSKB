FROM python:3

# Install django
RUN pip install --upgrade pip
RUN pip install django

# Add our Django files
ADD SSKB /opt/kb-app
WORKDIR /opt/kb-app

# Expose python server port
EXPOSE 8000

# Setup app
RUN python manage.py migrate

# Create superuser
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@localhost', 'password')" | python manage.py shell

# Start Django
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
