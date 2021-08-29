from copy import deepcopy
import re


def update_dict_fields(fields, **fields_mapping):
    updated_fields = dict(fields)
    for k, v in fields.items():
        if k in fields_mapping:
            updated_fields[k] = fields_mapping[k]
    return updated_fields


def clone(d): return deepcopy(d)


camel_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')
def camel_to_snake(string):
    return camel_case_pattern.sub('_', string).lower()
