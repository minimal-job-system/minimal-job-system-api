# Minimal Job System - API
Minimal Job System API is a minimalistic Django app for managing technology-independent jobs via a REST API.

Detailed documentation is in the "docs" directory.

## Quick start
1. Activate the Django virtual environment and install app via PIP::

    pip install .

2. Import a "job source" via the Django admin interface (you'll need the Admin app enabled)::

    Job_System_Api/Job sources/Add
    Job_System_Api/Job templates/; SYNCHRONIZE JOB SOURCES

3. Add users to the job system scope::

    Authentication and Authorization/Groups/Add; Name: jobsys
    Authentication and Authorization/Groups/Add; Groups: jobsys

4. Add the Minimal Job System API into a Django project site::

    <django_site>/settings.py
    INSTALLED_APPS [ ..., 'job_system_api' ]
    <django_site>/urls.py
    urlpatterns = [ ..., url(r'^api/', include('job_system_api.urls')) ]

5. Run `python manage.py migrate minimal_job_system_api` to create the Minimal Job System API models.

