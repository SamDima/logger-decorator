from logger_decorator import logger_decorator

@logger_decorator(event_type='simple_sync_fnc')
def another_sync_fnc(*args, **kwargs):
    return True

@logger_decorator(event_type='make_exception')
def except_func():
    1/0


def test_sync_func(caplog):
    @logger_decorator(event_type='sync_recursion_factorial_func', entry=True)
    def factorial_recursive(n):
        except_func()
        another_sync_fnc()
        if n == 1:
            return 1

        else:
            return n * factorial_recursive(n - 1)

    factorial_recursive(1)

    fields_to_assert = [
                        'Entry', 'Exit', 'level',
                        'request_id', 'event_type', 'func_result',
                        'error', 'duration_time', 'func_name',
                        'func_module',
                        'args',
                        'kwargs',
                        'kwargs',

                        ]
    for i in fields_to_assert:
        assert i in caplog.text


def test_sync_func_with_race(caplog):
    @logger_decorator(event_type='raise')
    def test_check_raice():
        raise Exception(400)

    test_check_raice()

    fields_to_assert = [
        'Exit', 'level',
        'request_id', 'event_type', 'func_result',
        'error', 'duration_time', 'func_name',
        'func_module',
        'args',
        'kwargs',
        'kwargs',

    ]
    for i in fields_to_assert:
        assert i in caplog.text

