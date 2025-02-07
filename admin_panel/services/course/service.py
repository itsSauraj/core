from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist

from admin_panel.models import Course, CourseModules, CourseModuleLessons, \
  UserCourseActivity, CourseCollection

from .serializer import ResponseCourseSerializer, ResponseModuleStructureSerializer, \
  CreateLessonRequestSerializer, CreateModuleRequestSerializer, CourseDataSerializer

from .dependencies import get_module_duration

class CourseAPIService:

  @staticmethod
  def get_course_by_id(course_id, created_by=None):
    try:
      course = Course.objects.get(id=course_id, created_by=created_by)
      return course
    except ObjectDoesNotExist:
      return None
        
  @staticmethod
  def get_all_collections(created_by=None):
    return CourseCollection.objects.all().filter(created_by=created_by)

  @staticmethod
  def get_all_courses(created_by=None):
    return Course.objects.all().filter(created_by=created_by)
  
  @staticmethod
  def get_assined_courses(user):
    return user
  
  @staticmethod
  def get_module_by_id(module_id):
    try:
      module = CourseModules.objects.get(id=module_id)
      return module
    except ObjectDoesNotExist:
      return None


  @staticmethod
  def get_course_modules(course_id, module_id=None):
    modules = CourseModules.objects.all().filter(course=course_id).filter(parent_module__id=module_id)
    for module in modules:
      module.duration = get_module_duration(module)
    return modules
  
  @staticmethod
  def get_all_module_contents(module):
    sub_modules = module.get_sub_modules
    lessons = module.get_all_lessons

    module.duration = get_module_duration(module)
    for sub_module in sub_modules:
      sub_module.duration = get_module_duration(sub_module)

    module_structure = {
      'metadata': module,
      'sub_modules': sub_modules,
      'lessons': lessons
    }

    serializer_data = ResponseModuleStructureSerializer(module_structure).data
    return serializer_data
  
      
  @staticmethod
  def get_all_module_contents_recursive(module):
    module_structure = {
      'tilte': module.title,
      'description': module.description,
      'duration': None,
      'sub_modules': [],
      'lessons': []
    }

    module_data = CreateModuleRequestSerializer(module).data 

    module_structure['title'] = module_data['title']
    module_structure['description'] = module_data['description']
    module_data['sequence'] = module_data['sequence']
    module_data['duration'] = get_module_duration(module)

    #lessson
    module_structure['lessons'] = CreateLessonRequestSerializer(module.get_all_lessons, many=True).data

    #sub modules
    sub_modules = module.get_sub_modules
    if sub_modules.count() > 0:
      for sub_module in sub_modules:
        module_structure['sub_modules'].append(CourseAPIService.get_all_module_contents_recursive(sub_module))

    return module_structure
  

  @staticmethod
  def import_course(request, data):
    course = CourseAPIService.create(request, data['course'])
    CourseAPIService.import_module(request, course, data['modules'])
    return course
  
  @staticmethod
  def import_module(request, course, modules, parent_module=None):
    for module in modules:
      created_module = CourseAPIService.create_module(request, course.id, parent_module, CreateModuleRequestSerializer(module).data)

      for lesson in module.get('lessons', []):
        lesson['module'] = created_module
        lesson['duration'] = timedelta(hours=int(lesson['hours']), 
                                      minutes=int(lesson['minutes']), 
                                      seconds=int(lesson['seconds']))
        CourseAPIService.create_lesson(request, course.id, created_module.id, CreateLessonRequestSerializer(lesson).data)

      if 'sub_modules' in module:
        CourseAPIService.import_module(request, course, module['sub_modules'], created_module)

    return True


  @staticmethod
  def create(request, data):
    course = Course.objects.create(**data)
    course.created_by = request.user
    course.save()
    return course
  
  @staticmethod
  def delete(request, course_id):
    course = CourseAPIService.get_course_by_id(course_id, request.user)
    course.delete()

  @staticmethod
  def update(request, course_id, data):
    course = CourseAPIService.get_course_by_id(course_id, request.user)

    for key, value in data.items():
      setattr(course, key, value)

    course.save()

    return course

  @staticmethod
  def create_module(request, course_id, parent_module, data):
    if parent_module:
      module = CourseModules(**data, course_id=course_id, parent_module_id=parent_module.id)
    else:
      module = CourseModules(**data, course_id=course_id)
    module.save()
    return module
  
  @staticmethod
  def delete_module(request, course_id, module_id):
    module = CourseModules.objects.get(id=module_id)
    module.delete()
  

  @staticmethod
  def create_lesson(request, course_id, module_id, data):
    course = CourseAPIService.get_course_by_id(course_id, request.user)
    module = CourseAPIService.get_module_by_id(module_id)

    if course is None or module is None:
      return None

    lesson = CourseModuleLessons(**data, course=course, module=module)
    lesson.save()
    return lesson

  @staticmethod
  def delete_lesson(request, lesson_id):
    lesson = CourseModuleLessons.objects.get(id=lesson_id)
    lesson.delete()


  @staticmethod
  def get_course_structure(course_id, user):
    course = CourseAPIService.get_course_by_id(course_id, user)
    metadata = ResponseCourseSerializer(course).data

    modules = course.get_all_modules()
    module_structure = []
    
    for module in modules:
      module_structure.append(CourseAPIService.get_all_module_contents_recursive(module))

    return {
      "id": metadata['id'],
      "title": metadata['title'],
      "description": metadata['description'],
      "duration": metadata['duration'],
      "image": metadata['image'],
      "modules": module_structure,
    }

  @staticmethod
  def start_user_course(data):
    user_course_activity, created = UserCourseActivity.objects.get_or_create(**data)
    return user_course_activity
  
  @staticmethod
  def course_is_started(course_id, user):
    return UserCourseActivity.objects.filter(course_id=course_id, user=user)