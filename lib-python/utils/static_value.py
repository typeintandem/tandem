def static_value(inner_function):
    value = None

    def outer_function(*args, **kwargs):
        nonlocal value

        if value is None:
            value = inner_function(*args, **kwargs)

        return value

    return outer_function
