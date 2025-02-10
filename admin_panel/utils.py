import os
import uuid

def rename_file(instance, filename):

    instance_name = instance.__class__.__name__.lower()

    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(f'uploads/{instance_name}', new_filename)