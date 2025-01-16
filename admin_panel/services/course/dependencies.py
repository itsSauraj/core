from datetime import timedelta


def get_module_duration(module):
  duration = timedelta(seconds=0)
  for sub_module in module.get_sub_modules:
    duration += get_module_duration(sub_module)

  for lesson in module.get_all_lessons:
    duration += lesson.duration

  return duration

def get_course_duration(course):
  duration = timedelta(seconds=0)
  for module in course.get_all_modules():
    duration += get_module_duration(module)

  return duration


def get_all_module_contents(module):
  sub_modules = []
  for sub_module in module.get_sub_modules:
    sub_modules.append(get_all_module_contents(sub_module))

  lessons = module.get_all_lessons
  return {
    'metadata': module,
    'sub_modules': sub_modules,
    'lessons': lessons
  }