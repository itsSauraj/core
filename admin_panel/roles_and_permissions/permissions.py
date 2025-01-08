from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

CustomPermissionContentType = "custom_permission"
CustomPermissionModel = "app_permissions"

class Module:
    COURSES = 'Courses'
    MENTORS = 'Mentors'
    TRAINEES = 'Trainees'
    PERMISSIONS = 'Permissions'
    ROLES = 'Roles'

    ALL_MODULES = [MENTORS, TRAINEES, COURSES, PERMISSIONS, ROLES]

class PERM:
    name = ''
    module = ''
    codename = ''

    def key(self):
        return f"{CustomPermissionContentType}.{self.codename}"

    def __init__(self, name, module, codename):
        self.codename = codename
        self.name = name
        self.module = module

class PermissionManager:
    
    # MENTOTRS
    MENTOR_CREATE = PERM(name='Create', module=Module.MENTORS, codename='mentors.create')
    MENTOR_EDIT = PERM(name='Edit', module=Module.MENTORS, codename='mentors.edit')
    MENTOR_DELETE = PERM(name='Delete', module=Module.MENTORS, codename='mentors.delete')
    MENTOR_VIEW = PERM(name='View', module=Module.MENTORS, codename='mentors.view')
    
    # TRINEES
    TRAINEE_CREATE = PERM(name='Create', module=Module.TRAINEES, codename='trainees.create')
    TRAINEE_EDIT = PERM(name='Edit', module=Module.TRAINEES, codename='trainees.edit')
    TRAINEE_DELETE = PERM(name='Delete', module=Module.TRAINEES, codename='trainees.delete')
    TRAINEE_VIEW = PERM(name='View', module=Module.TRAINEES, codename='trainees.view')

    # COURSES
    COURSES_CREATE = PERM(name='Create', module=Module.COURSES, codename='courses.create')
    COURSES_VIEW = PERM(name='View', module=Module.COURSES, codename='courses.view')
    COURSES_EDIT = PERM(name='Edit', module=Module.COURSES, codename='courses.edit')
    COURSES_DELETE = PERM(name='Delete', module=Module.COURSES, codename='courses.delete')

    # ROLES
    ROLES_CREATE = PERM(name='Create', module=Module.ROLES, codename='roles.create')
    ROLES_VIEW = PERM(name='View', module=Module.ROLES, codename='roles.view')
    ROLES_EDIT = PERM(name='Edit', module=Module.ROLES, codename='roles.edit')
    ROLES_DELETE = PERM(name='Delete', module=Module.ROLES, codename='roles.delete')

    # PERMISSIONS
    PERMISSIONS_CREATE = PERM(name='Create', module=Module.PERMISSIONS, codename='permissions.create')
    PERMISSIONS_VIEW = PERM(name='View', module=Module.PERMISSIONS, codename='permissions.view')
    PERMISSIONS_EDIT = PERM(name='Edit', module=Module.PERMISSIONS, codename='permissions.edit')
    PERMISSIONS_DELETE = PERM(name='Delete', module=Module.PERMISSIONS, codename='permissions.delete')


    ALL_PERMS = [
        MENTOR_CREATE,
        MENTOR_EDIT,
        MENTOR_DELETE,
        MENTOR_VIEW,
        TRAINEE_CREATE,
        TRAINEE_EDIT,
        TRAINEE_DELETE,
        TRAINEE_VIEW,
        COURSES_CREATE,
        COURSES_VIEW,
        COURSES_EDIT,
        COURSES_DELETE,
        ROLES_CREATE,
        ROLES_VIEW,
        ROLES_EDIT,
        ROLES_DELETE,
        PERMISSIONS_CREATE,
        PERMISSIONS_VIEW,
        PERMISSIONS_EDIT,
        PERMISSIONS_DELETE,
    ]

    ALL_PERM_CODES = [perm.codename for perm in ALL_PERMS]
    CODES_TO_PERM = {p.codename: p for p in ALL_PERMS}
    CODES_TO_MODULE_NAME = {p.codename: p.module for p in ALL_PERMS}

    def get_permissions_by_ids(self, ids):
        return Permission.objects.filter(pk__in=ids)

    def get_name_by_ids(self, ids):
        return [perm['codename'] for perm in 
                Permission.objects.filter(pk__in=ids).values('codename')]
    
    def refresh_permissions_in_store(self):
        # Ensure content type exists
        content_type, created = ContentType.objects.get_or_create(
            app_label=CustomPermissionContentType, model=CustomPermissionModel)

        db_perm_list = [p['codename'] for p in
                        Permission.objects.filter(
                            content_type__app_label=CustomPermissionContentType)
                            .values('codename')]
        current_perm_codes = self.ALL_PERM_CODES
        new_perm_list = [p for p in current_perm_codes if p not in db_perm_list]

        content_type = ContentType.objects.get(app_label=CustomPermissionContentType)

        for perm_code in new_perm_list:
            perm = self.CODES_TO_PERM[perm_code]
            Permission.objects.create(name=perm.name, codename=perm.codename,
                                    content_type=content_type)

    def get_all_system_permissions(self):
        permissions = Permission.objects.filter(codename__in=self.ALL_PERM_CODES,
                                        content_type__app_label=CustomPermissionContentType)
        self.populate_module_name(permissions)
        return permissions

    def populate_module_name(self, permissions):
        for p in permissions:
            p.module = self.CODES_TO_MODULE_NAME[p.codename]

    def get_perms_for_create(self):
        perms_from_db = Permission.objects.filter(codename__in=self.ALL_PERM_CODES,
                                        content_type__app_label=CustomPermissionContentType)

        codename_to_perm_id = {p.codename: p.id for p in perms_from_db}

        module_to_perms = {}
        for perm in self.ALL_PERMS:
            if perm.module not in module_to_perms:
                module_to_perms[perm.module] = []
            perm.id = codename_to_perm_id[perm.codename]
            module_to_perms[perm.module].append(perm)
        return module_to_perms


permission_manager = PermissionManager()
