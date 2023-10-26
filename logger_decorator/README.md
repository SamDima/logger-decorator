#  Logger Decorator

    Logger Decorator can log sync/async/yield (sync/async) functions. 
    
    Can pass unique request id for all functions to have possibility ease find in your log all operations by filtering request_id.
    
    Use as simple python decorator

    if you need alerting to slack you can use @LoggerDecorator intead of @logger_decorator
    @LoggerDecorator(
        event_type='main_func',
        full_trace=True,
        webhook_url=<you_url>',
        entry=True,
        notification_slack=True
        )

## Getting started
    1. pip install logger_decorator
    1.1 import: from logger_decorator import logger_decorator
    1.2 If function return yield need to pass yield_=True
    1.3 Decorator need to be placed last
    1.4 To generate unique request_id  you need use  middleware
# Example middleware usage (Fast Api)

    @app.middleware("http")
        async def log_request(request: Request, call_next):
            set_request_id() # to create unique request_id
            response: responses.StreamingResponse = await call_next(request)
            return response

# Usage with Threads to pass request_id
    1. To pass request_id use <kwargs> kwargs = {'request_id': get_request_id_()}

# To use with Celery and pass request_id from your app to celery
    celery_task.apply_async(args=(ar,), kwargs={'request_id': get_request_id_()})

# Usage with celery Beat
           celery.conf.beat_schedule = {
               'call-every-10-seconds': {
               'task': 'my_schedule_task',
               'schedule': 10.0, #time-interval type
           }
        
           @logger_decorator(event_type='task1')
           def task1(*args, **kwargs):
               pass
        
           @logger_decorator(event_type='task2')
           def task2(*args, **kwargs):
               pass
        
    
        @celery.task(name='my_schedule_task') 
        def my_schedule_task(*args, **kwargs):
            set_request_id() # create request_id
            task1(request_id=get_request_id_())
            task2(request_id=get_request_id_())


# Usage with Django
    <middlewary.py>
    from logger_decorator import set_request_id

    class MyMiddleware:
        def __init__(self, get_response):
            set_request_id() # initializations request_id
            self._get_response = get_response
    
        def __call__(self, request):
            response = self._get_response(request)
            set_request_id() # initializations request_id
            return response
    
    <serializers.py>
    from rest_framework import serializers
    from main.models import Book
    from logger_decorator import logger_decorator
    
    @logger_decorator(event_type='helper_func')
    def helper_func():
        return 'ok'
    
    
    class BookModelSerializer(serializers.ModelSerializer):
    
        title = serializers.SerializerMethodField()
    
        @logger_decorator(event_type='get_title')
        def get_title(self, obj):
            helper_func()
            return obj.title
    
        class Meta:
            model = Book
            fields = '__all__'

