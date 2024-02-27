import os
from rest_framework import exceptions


def validate_file(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf',  '.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise exceptions.ValidationError('Only pdf and image files are supported')
    file_size = value.size
    if ext.lower() == '.pdf':
        megabyte_limit = 5.0
        if file_size > megabyte_limit * 1024 * 1024:
            raise exceptions.ValidationError(f"Max size of document you can upload is {megabyte_limit} MB")
    else:
        megabyte_limit = 15.0
        if file_size > megabyte_limit * 1024 * 1024:
            raise exceptions.ValidationError(f"Max size of image you can upload is {megabyte_limit} MB")
