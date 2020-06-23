from django.contrib import admin

from .models import Alumni,CourseCompletion,User,AlumniProfile,ManuelVerification

class AlumniAdmin(admin.ModelAdmin):
    list_display = ('user','department','batch','contact','verify_status')

class CourseCompletionAdmin(admin.ModelAdmin):
    list_display = ('periods','number_of_students','number_of_graduates','number_of_placed')

    def periods(self,obj):
        return str(obj.start.year) + " - " + str(obj.end.year)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email','is_active','is_alumni','is_student','is_admin')


class ManuelVerificationAdmin(admin.ModelAdmin):
    list_display = ('alumni','verification_file','verify_status','request_date')
    def verification_file(self,obj):
        return obj.alumni.verification_file
        
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ('bio','work','organization','linkedin','twitter','facebook','private')


admin.site.register(Alumni,AlumniAdmin)
admin.site.register(CourseCompletion,CourseCompletionAdmin)
admin.site.register(User,UserAdmin)
admin.site.register(AlumniProfile,AlumniProfileAdmin)
admin.site.register(ManuelVerification,ManuelVerificationAdmin)
