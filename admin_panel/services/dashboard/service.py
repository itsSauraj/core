from .serilaizer import InfoCardSerializer

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
