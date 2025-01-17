import os
import uuid

def rename_file(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/course_collection', new_filename)