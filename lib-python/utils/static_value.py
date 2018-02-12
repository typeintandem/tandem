def static_value(inner_function):
    dict_value = {}  # Using dictionary to workaround Python2's lack of `nonlocal`

    def outer_function(*args, **kwargs):
        if dict_value.get('value', None) is None:
            dict_value['value'] = inner_function(*args, **kwargs)

        return dict_value['value']

    return outer_function
