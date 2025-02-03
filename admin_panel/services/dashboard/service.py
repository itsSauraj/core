from .serilaizer import InfoCardSerializer, CourseCompletionStatusSerializer

class DashboardService:
  
  @staticmethod
  def getInfoCardsData(user):
    mentors = user.get_created_mentors()
    trainees = user.get_created_trainees()
    courses = user.get_created_courses()
    collections = user.get_created_collections()

    context = [
      {
        "title": "Mentors",
        "count": mentors.count()
      },
      {
        "title": "Trainees",
        "count": trainees.count()
      },
      {
        "title": "Courses",
        "count": courses.count()
      },
      {
        "title": "Collections",
        "count": collections.count()
      }
    ]

    return InfoCardSerializer(context, many=True).data

  @staticmethod
  def getCourseDetails(user, call):
    courses_collection = user.collections.all()
    
    context = []

    for collection in courses_collection:
      data = { "course": collection.title + str(call), "enrolled": 0, "completed": 0, "in_progress": 0, "not_started": 0 }
      enrollements = collection.enrollments()
      data["enrolled"] = enrollements.count()
      for enrollment in enrollements:
        if enrollment.completed_on:
          data["completed"] += 1
        elif enrollment.started_on: 
          data["in_progress"] += 1
        else:
          data["not_started"] += 1
      context.append(data)

    return CourseCompletionStatusSerializer(context, many=True).data
