from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(self,request,view_func,view_args,view_kwargs):
        modulename=view_func.__module__
        print(modulename)
        user=request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "student_management_app.HodViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                elif modulename == "django.contrib.auth.views" or modulename =="django.contrib.admin.sites":
                    pass
                else:
                    return HttpResponseRedirect(reverse("admin_home"))
            elif user.user_type == "2":
                if modulename == "student_management_app.ProfesseurViews" or modulename == "student_management_app.EditResultVIewClass":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("professeur_home"))
            elif user.user_type == "3":
                if modulename == "student_management_app.StudentViews" or modulename == "django.views.static":
                    pass
                elif modulename == "student_management_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            elif user.user_type == "4":
                if modulename == "student_management_app.EconomeViews" or modulename == "django.views.static":
                    pass
                elif modulename == "student_management_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            elif user.user_type == "5":
                if modulename == "student_management_app.SecretaireViews" or modulename == "django.views.static":
                    pass
                elif modulename == "student_management_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            elif user.user_type == "6":
                if modulename == "student_management_app.SurveillantViews" or modulename == "django.views.static":
                    pass
                elif modulename == "student_management_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            elif user.user_type == "7":
                if modulename == "student_management_app.BibliothequeViews" or modulename == "django.views.static":
                    pass
                elif modulename == "student_management_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            elif user.user_type == "8":
                if modulename == "student_management_app.CantineViews" or modulename == "django.views.static":
                    pass
                elif modulename == "student_management_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            elif user.user_type == "9":
                if modulename == "student_management_app.MedecineViews" or modulename == "django.views.static":
                    pass
                elif modulename == "student_management_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            else:
                return HttpResponseRedirect(reverse("show_login"))

        else:
            if request.path == reverse("show_login") or request.path == reverse("do_login") or modulename == "django.contrib.auth.views" or modulename =="django.contrib.admin.sites" or modulename=="student_management_app.views":
                pass
            else:
                return HttpResponseRedirect(reverse("show_login"))
            
            