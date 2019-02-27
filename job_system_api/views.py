from datetime import timedelta
from django_filters import rest_framework
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import etag, condition
from rest_framework import generics, filters

from job_system_api.models import JobTemplate, Job, JobParameter, JobLogEntry
from job_system_api.models import JOB_TYPE_CHOICES
from job_system_api.serializers import JobTemplateSerializer, JobSerializer, \
    JobDetailsSerializer, JobParameterSerializer, JobLogEntrySerializer


class JobTemplateListView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = JobTemplate.objects.all()
    serializer_class = JobTemplateSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new job template."""
        serializer.save()


class JobTemplateDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    # @see rest_framework/generics.py, line 77
    lookup_url_kwarg = 'templ_id'  # capturing group of the url pattern
    lookup_field = 'id'  # primary key of the model

    queryset = JobTemplate.objects.all()
    serializer_class = JobTemplateSerializer


class JobFilter(rest_framework.FilterSet):
    type_name = rest_framework.CharFilter(
        label="Type name", method="filter_type_name"
    )
    days_since_creation = rest_framework.NumberFilter(
        label="Days since creation", method="filter_days_since_creation"
    )

    class Meta:
        model = Job
        fields = [
            'id', 'namespace', 'name', 'type_name', 'type', 'status',
            'progress', 'owner', 'days_since_creation'
        ]

    def filter_type_name(self, queryset, name, value):
        type = [
            choice_key for choice_key, choice_value in JOB_TYPE_CHOICES
            if choice_value == value
        ]
        return queryset.filter(
            type=type[0] if len(type) == 1 else -1
        )

    def filter_days_since_creation(self, queryset, name, value):
        if value is None or value != int(value):  # check if value is an integer
            return queryset
        else:
            return queryset.filter(
                Q(date_modified__date__gte=timezone.now()-timedelta(days=int(value)))
            )


class JobListView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = (rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = JobFilter
    filter_fields = ('type', 'status')
    ordering = ('-date_created',)
    ordering_fields = ('type', 'status', 'date_created')

    def perform_create(self, serializer):
        """Save the post data when creating a new job."""
        serializer.save()


class JobDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    # @see rest_framework/generics.py, line 77
    lookup_url_kwarg = 'job_id'  # capturing group of the url pattern
    lookup_field = 'id'  # primary key of the model

    queryset = Job.objects.all()
    serializer_class = JobDetailsSerializer

    def get(self, request, *args, **kwargs):
        etag_func = (
            lambda request, *args, **kwargs:
                str(hash(Job.objects.get(pk=kwargs['job_id'])))
        )
        last_modified_func = (
            lambda request, *args, **kwargs:
                Job.objects.get(pk=kwargs['job_id']).date_modified
        )
        @condition(
            etag_func=etag_func,
            last_modified_func=last_modified_func
        )
        def _get(request, *args, **kwargs):
            return generics.RetrieveUpdateDestroyAPIView.get(
                self, request, *args, **kwargs
            )
        return _get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        etag_func = (
            lambda request, *args, **kwargs:
                str(hash(Job.objects.get(pk=kwargs['job_id'])))
        )
        last_modified_func = (
            lambda request, *args, **kwargs:
                Job.objects.get(pk=kwargs['job_id']).date_modified
        )
        @condition(
            etag_func=etag_func,
            last_modified_func=last_modified_func
        )
        def _put(request, *args, **kwargs):
            return generics.RetrieveUpdateDestroyAPIView.put(
                self, request, *args, **kwargs
            )
        return _put(request, *args, **kwargs)


class JobParameterListView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    serializer_class = JobParameterSerializer

    def get_queryset(self):
        queryset = JobParameter.objects.all()
        job_id = self.kwargs['job_id']
        return queryset.filter(job=job_id)

    def perform_create(self, serializer):
        """Save the post data when creating a new job parameter."""
        serializer.save(job=Job.objects.get(pk=self.kwargs['job_id']))


class JobParameterDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    # @see rest_framework/generics.py, line 77
    lookup_url_kwarg = 'parameter_id'  # capturing group of the url pattern
    lookup_field = 'id'  # primary key of the model

    serializer_class = JobParameterSerializer

    def get_queryset(self):
        return JobParameter.objects.filter(
            job=self.kwargs['job_id']
        )

    def perform_update(self, serializer):
        serializer.save(job=Job.objects.get(pk=self.kwargs['job_id']))


class JobLogEntryListView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    serializer_class = JobLogEntrySerializer

    def get_queryset(self):
        queryset = JobLogEntry.objects.all()
        job_id = self.kwargs['job_id']
        return queryset.filter(job=job_id)

    def perform_create(self, serializer):
        """Save the post data when creating a new log entry."""
        serializer.save(job=Job.objects.get(pk=self.kwargs['job_id']))


class JobLogEntryDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    # @see rest_framework/generics.py, line 77
    lookup_url_kwarg = 'log_id'  # capturing group of the url pattern
    lookup_field = 'id'  # primary key of the model

    serializer_class = JobLogEntrySerializer

    def get_queryset(self):
        return JobLogEntry.objects.filter(
            job=self.kwargs['job_id']
        )

    def perform_update(self, serializer):
        serializer.save(job=Job.objects.get(pk=self.kwargs['job_id']))
