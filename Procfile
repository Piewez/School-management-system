web: gunicorn student_management_system.wsgi --log-file -
#or works good with external database
web: python manage.py migrate && gunicorn student_management_system.wsgi