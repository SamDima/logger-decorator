import json
import traceback
import uuid
import time
import inspect
import functools
from typing import Dict

import requests

from loguru import logger
from contextvars import ContextVar, Token

req_id_default = str(uuid.uuid4())

REQUEST_ID_CTX_KEY = 'request_id'
REQUEST_ADDITIONAL_CTX_KEY = 'additional_info'
WEBHOOK_URL = 'webhook_url'

_request_id_ctx_var: ContextVar[str] = ContextVar(REQUEST_ID_CTX_KEY, default=req_id_default)
_request_additional_var: ContextVar[any] = ContextVar(REQUEST_ADDITIONAL_CTX_KEY, default=None)
_webhook_url_slack: ContextVar[str] = ContextVar('_webhook_url_slack', default=None)
_log_data: ContextVar[Dict[str, str]] = ContextVar('_log_data', default=None)
_log_link: ContextVar[str] = ContextVar('_log_link', default=None)


def set_request_id() -> Token[str]:
    request_id = _request_id_ctx_var.set(str(uuid.uuid4()))
    return request_id


def get_request_id_(*args) -> str:
    return _request_id_ctx_var.get(*args)


def reset_request_id(request_id):
    return _request_id_ctx_var.reset(request_id)


def get_add_info():
    return _request_additional_var.get()


def get_error(e, full_trace=False):
    error_text = e
    try:
        error_text = e.detail
    except AttributeError:
        error_text = error_text
    trace = traceback.format_exc()
    error = trace if full_trace else error_text
    result = e
    level = "ERROR"
    return trace, error, result, level


class Notification:

    @staticmethod
    def send_message_to_slack_webhook(log_info):
        event_type = log_info.get('Exit').get('event_type')
        slack_data = {'text': str({'Message': f'Something wrong with {event_type}, see logs by request_id',
                                   'request_id':_request_id_ctx_var.get(),
                                   'log_link': _log_link.get(),
                                   'short trace': log_info.get('Exit').get('func_result')
                                   }
                                  )}
        requests.post(
            _webhook_url_slack.get(), data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )


class Ctx:

    def __init__(self):
        self.ctx = {}

    def log_add_info(self, **kwargs):
        for k, v in kwargs.items():
            self.ctx[k] = v
        _request_additional_var.set(self.ctx)

    def get_add_info(self):
        _request_additional_var.get()

    @staticmethod
    def reset_add_info(var):
        _request_additional_var.reset(var)

    @staticmethod
    def get_info():
        return get_add_info()

    @classmethod
    def get_log(cls,
                level='INFO',
                entry_point=None,
                request_id=None,
                event_type=None,
                result=None,
                error=None,
                duration=None,
                func_name=None,
                func_module=None,
                args=None,
                kwargs=None,
                ):
        log_dct = {entry_point: {
            'level': f"{level}",
            'request_id': f"{request_id}",
            'event_type': f"{event_type}",
            'func_result': f"{result}",
            'error': f"{error}",
            'duration_time': f"{duration}",
            'func_name': f"{func_name}",
            'func_module': f"{func_module}",
            'args': f"{args}",
            'kwargs': f"{kwargs}",
            'add_info': f"{_request_additional_var.get()}"
        }
        }
        return log_dct


def logger_decorator(event_type=None, *, full_trace=False, entry=False, exit=True, yield_=False, webhook_url=None, notification_slack=None, **kwargs):
    _webhook_url_slack.set(webhook_url)

    def wrapper(func):
        if yield_:
            if inspect.isasyncgenfunction(func):
                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    s_time = time.time()
                    async for i in func():
                        result = yield i
                    e_time = time.time()
                    duration = e_time - s_time

                    logger_ = logger.opt(depth=1)
                    level = "INFO"
                    error = None

                    if kwargs.get('request_id'):
                        request_id = kwargs.get('request_id')
                    else:
                        request_id = get_request_id_()
                    log_info = Ctx.get_log(
                        level=level,
                        entry_point='Exit',
                        request_id=request_id,
                        event_type=event_type,
                        result=result if not error else error,  # noqa
                        duration=duration,
                        func_name=func.__name__,
                        func_module=func.__module__,
                        args=args,
                        kwargs=kwargs,
                    )

                    if error:
                        if notification_slack:
                            Notification.send_message_to_slack_webhook(log_info)

                    if exit:
                        logger_.log(level, log_info)

                    _request_additional_var.set(None)

                return wrapper
            else:
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    s_time = time.time()
                    result = yield from func()
                    e_time = time.time()
                    duration = e_time - s_time
                    logger_ = logger.opt(depth=1)
                    level = "INFO"
                    error = None

                    if kwargs.get('request_id'):
                        request_id = kwargs.get('request_id')
                    else:
                        request_id = get_request_id_()
                    log_info = Ctx.get_log(
                        level=level,
                        entry_point='Exit',
                        request_id=request_id,
                        event_type=event_type,
                        result=result if not error else error,
                        duration=duration,
                        func_name=func.__name__,
                        func_module=func.__module__,
                        args=args,
                        kwargs=kwargs,
                    )

                    if error:
                        if notification_slack:
                            Notification.send_message_to_slack_webhook(log_info)

                    if exit:
                        logger_.log(level, log_info)

                    _request_additional_var.set(None)
                    return result

                return wrapper

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                duration = None
                logger_ = logger.opt(depth=1)
                level = "INFO"
                error = None

                if kwargs.get('request_id'):
                    request_id = kwargs.get('request_id')
                else:
                    request_id = get_request_id_()

                if entry:
                    log_info = Ctx.get_log(
                        level=level,
                        entry_point='Entry',
                        request_id=request_id,
                        event_type=event_type,
                        duration=duration,
                        error=error,
                        func_name=func.__name__,
                        func_module=func.__module__,
                        args=args,
                        kwargs=kwargs,
                    )

                    logger_.log(level, log_info)

                try:
                    start = time.time()
                    result = await func(*args, **kwargs)
                    end = time.time()
                    duration = end - start
                except Exception as e:
                    trace, error,  result, level = get_error(e, full_trace=full_trace)

                log_info = Ctx.get_log(
                    level=level,
                    entry_point='Exit',
                    request_id=request_id,
                    event_type=event_type,
                    result=result if not error else error,
                    duration=duration,
                    func_name=func.__name__,
                    func_module=func.__module__,
                    args=args,
                    kwargs=kwargs,
                )

                if error:
                    if notification_slack:
                        Notification.send_message_to_slack_webhook(log_info)

                if exit:
                    logger_.log(level, log_info)

                _request_additional_var.set(None)

                return result

            return wrapped
        else:
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                duration = None
                logger_ = logger.opt(depth=1)
                level = "INFO"
                error = None

                if kwargs.get('request_id'):
                    request_id = kwargs.get('request_id')
                else:
                    request_id = get_request_id_()

                if entry:
                    log_info = Ctx.get_log(
                        level=level,
                        entry_point='Entry',
                        request_id=request_id,
                        event_type=event_type,
                        duration=duration,
                        error=error,
                        func_name=func.__name__,
                        func_module=func.__module__,
                        args=args,
                        kwargs=kwargs,
                    )

                    logger_.log(level, log_info)

                try:
                    start = time.time()
                    result = func(*args, **kwargs)
                    end = time.time()
                    duration = end - start
                except Exception as e:
                    trace, error,  result, level = get_error(e, full_trace=full_trace)

                log_info = Ctx.get_log(
                    level=level,
                    entry_point='Exit',
                    request_id=request_id,
                    event_type=event_type,
                    result=result if not error else error,
                    duration=duration,
                    func_name=func.__name__,
                    func_module=func.__module__,
                    args=args,
                    kwargs=kwargs,
                )

                if error:
                    if notification_slack:
                        _log_data.set(log_info)
                        Notification.send_message_to_slack_webhook(log_info)


                if exit:
                    logger_.log(level, log_info)

                _request_additional_var.set(None)

                return result

            return wrapped

    return wrapper


class LoggerDecorator:
    def __init__(self, event_type=None, full_trace=None, webhook_url=None, entry=False, exit=True, yield_=False, notification_slack=True):
        self.event_type = event_type
        self.full_trace = full_trace
        self.webhook_url = webhook_url
        self.entry = entry
        self.exit = exit
        self.yield_ = yield_
        self.notification_slack = notification_slack


    def __call__(self, func):
        return logger_decorator(event_type=self.event_type,
                                full_trace=self.full_trace,
                                webhook_url=self.webhook_url,
                                entry=self.entry,
                                exit=self.exit,
                                notification_slack=self.notification_slack
                                )(func)
