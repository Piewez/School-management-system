"""student_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from student_management_app import views, HodViews, ProfesseurViews, StudentViews
from student_management_app.EditResultVIewClass import EditResultViewClass
from student_management_system import settings

urlpatterns = [
    path('demo',views.showDemoPage),
    path('signup_admin',views.signup_admin,name="signup_admin"),
    path('signup_student',views.signup_student,name="signup_student"),
    path('signup_professeur',views.signup_professeur,name="signup_professeur"),
    path('do_admin_signup',views.do_admin_signup,name="do_admin_signup"),
    path('do_professeur_signup',views.do_professeur_signup,name="do_professeur_signup"),
    path('do_signup_student',views.do_signup_student,name="do_signup_student"),
    path('admin/', admin.site.urls),
    path('accounts/',include('django.contrib.auth.urls')),
    path('',views.ShowLoginPage,name="show_login"),
    path('get_user_details', views.GetUserDetails),
    path('logout_user', views.logout_user,name="logout"),
    path('doLogin',views.doLogin,name="do_login"),
    path('admin_home',HodViews.admin_home,name="admin_home"),
    
    path('add_anneescolaire', HodViews.add_anneescolaire,name="add_anneescolaire"),
    path('add_anneescolaire_save', HodViews.add_anneescolaire_save,name="add_anneescolaire_save"),
    path('add_periode', HodViews.add_periode,name="add_periode"),
    path('add_periode_save', HodViews.add_periode_save,name="add_periode_save"),
    
    path('add_categorie_matiere', HodViews.add_categorie_matiere,name="add_categorie_matiere"),
    path('add_categorie_matiere_save', HodViews.add_categorie_matiere_save,name="add_categorie_matiere_save"),
    
    path('add_note/<str:classe_id>', HodViews.add_note,name="add_note"),
    path('view_note/<int:classe_id>/', HodViews.view_note, name='view_note'),
    path('view_classe_results/<int:classe_id>/', HodViews.view_classe_results, name='view_classe_results'),
    path('view_studen_results/<int:trimestre_id>/<int:eleve_id>/', HodViews.view_studen_results, name='view_studen_results'),
    path('create_note/<str:eleve_id>', HodViews.create_note,name="create_note"),
    path('delete-note/<int:note_id>/', HodViews.delete_note, name='delete_note'),
    path('edit-note/<int:note_id>/', HodViews.edit_note, name='edit_note'),
    
    path('generate_bulletin_pdf/<int:trimestre_id>/<int:eleve_id>/', HodViews.generate_bulletin_pdf, name='generate_bulletin_pdf'),
    path('resultat_classe_pdf/<int:trimestre_id>/<int:classe_id>/', HodViews.resultat_classe_pdf, name='resultat_classe_pdf'),
    path('statistique_classe_pdf/<int:trimestre_id>/<int:classe_id>/', HodViews.statistique_classe_pdf, name='statistique_classe_pdf'),
    path('generate_graphique_pdf/<int:trimestre_id>/<int:classe_id>/', HodViews.generate_graphique_pdf, name='generate_graphique_pdf'),
    path('download_class_reports/<int:trimestre_id>/<int:classe_id>/', HodViews.download_class_reports, name='download_class_reports'),
    path('resultat_annuel_classe/<int:classe_id>/', HodViews.resultat_annuel_classe, name='resultat_annuel_classe'),
    path('resultat_annuel_classe_pdf/<int:classe_id>/', HodViews.resultat_annuel_classe_pdf, name='resultat_annuel_classe_pdf'),
    
    path('generate_student_card/<int:student_id>/', HodViews.generate_student_card_pdf, name='generate_student_card'),
    path('generate_class_student_cards/<int:classe_id>/', HodViews.generate_class_student_cards_pdf, name='generate_class_student_cards'),
    
    path('enregistrer_comportement/<int:student_id>/', HodViews.enregistrer_comportement, name='enregistrer_comportement'),
    path('scanner_qr_code/<int:student_id>/', HodViews.scanner_qr_code, name='scanner_qr_code'),
    path('afficher_points/<int:student_id>/', HodViews.afficher_points, name='afficher_points'),
    
    
    path('add_econome',HodViews.add_econome,name="add_econome"),
    path('add_econome_save',HodViews.add_econome_save,name="add_econome_save"),

    
    path('add_professeur',HodViews.add_professeur,name="add_professeur"),
    path('add_professeur_save',HodViews.add_professeur_save,name="add_professeur_save"),
    path('add_classe/', HodViews.add_classe,name="add_classe"),
    path('add_classe_save', HodViews.add_classe_save,name="add_classe_save"),
    path('add_student', HodViews.add_student,name="add_student"),
    path('add_student_save', HodViews.add_student_save,name="add_student_save"),
    path('add_matiere', HodViews.add_matiere,name="add_matiere"),
    path('add_matiere_classe', HodViews.add_matiere_classe,name="add_matiere_classe"),
    path('add_matiere_save', HodViews.add_matiere_save,name="add_matiere_save"),
    
    path('add_examen_blanc', HodViews.add_examen_blanc,name="add_examen_blanc"),
    
    path('examen/<int:examen_blanc_id>/eleves/', HodViews.afficher_eleves_concernes, name='afficher_eleves_concernes'),
    path('liste-eleve-examen-generate-pdf/<int:examen_blanc_id>/', HodViews.list_eleve_examen_generate_pdf, name='list_eleve_examen_generate_pdf'),
    
    
    path('manage_examen', HodViews.manage_examen,name="manage_examen"),
    path('choose_examen_to_add_note', HodViews.choose_examen_to_add_note,name="choose_examen_to_add_note"),
    path('choose_examen_to_view_note', HodViews.choose_examen_to_view_note,name="choose_examen_to_view_note"),
    path('choose_examen_to_view_results', HodViews.choose_examen_to_view_results,name="choose_examen_to_view_results"),
    path('add_note_Examen/<int:examen_blanc_id>/', HodViews.add_note_Examen,name="add_note_Examen"),
    path('view_note_Examen/<int:examen_blanc_id>/', HodViews.view_note_Examen,name="view_note_Examen"),
    path('view_exam_results/<int:examen_blanc_id>/', HodViews.view_exam_results,name="view_exam_results"),
    path('resultat_examen_pdf/<int:examen_blanc_id>/', HodViews.resultat_examen_pdf,name="resultat_examen_pdf"),
    
    path('manage_econome', HodViews.manage_econome,name="manage_econome"),
    
    path('manage_professeur', HodViews.manage_professeur,name="manage_professeur"),
    path('manage_student', HodViews.manage_student,name="manage_student"),
    path('manage_classe', HodViews.manage_classe,name="manage_classe"),
    path('manage_matiere', HodViews.manage_matiere,name="manage_matiere"),
    path('manage_matiere_classe/<str:classe_id>', HodViews.manage_matiere_classe,name="manage_matiere_classe"),
    path('manage_anneescolaire', HodViews.manage_anneescolaire,name="manage_anneescolaire"),
    path('manage_periode', HodViews.manage_periode,name="manage_periode"),
    path('manage_categorie', HodViews.manage_categorie,name="manage_categorie"),
    
    path('choose_Classe_To_Add_Notes', HodViews.choose_Classe_To_Add_Notes,name="choose_Classe_To_Add_Notes"),
    path('choose_Classe_To_View_Notes', HodViews.choose_Classe_To_View_Notes,name="choose_Classe_To_View_Notes"),
    path('choose_Classe_To_View_Results', HodViews.choose_Classe_To_View_Results,name="choose_Classe_To_View_Results"),
    
    path('delete_matiere/<int:matiere_id>/', HodViews.delete_matiere, name='delete_matiere'),
    path('delete_professeur/<int:professeur_id>/', HodViews.delete_professeur, name='delete_professeur'),
    path('delete_econome/<int:econome_id>/', HodViews.delete_econome, name='delete_econome'),
    path('delete_classe/<int:classe_id>/', HodViews.delete_classe, name='delete_classe'),
    
    
    
    path('edit_anneescolaire/<str:anneescolaire_id>', HodViews.edit_anneescolaire,name="edit_anneescolaire"),
    path('edit_anneescolaire_save', HodViews.edit_anneescolaire_save,name="edit_anneescolaire_save"),
    path('edit_periode/<str:periode_id>', HodViews.edit_periode,name="edit_periode"),
    path('edit_periode_save', HodViews.edit_periode_save,name="edit_periode_save"),
    path('edit_categorie_matiere/<str:categorie_matiere_id>', HodViews.edit_categorie_matiere,name="edit_categorie_matiere"),
    path('edit_categorie_matiere_save', HodViews.edit_categorie_matiere_save,name="edit_categorie_matiere_save"),
    
    
    
    path('edit_professeur/<str:professeur_id>', HodViews.edit_professeur,name="edit_professeur"),
    path('edit_professeur_save', HodViews.edit_professeur_save,name="edit_professeur_save"),
    path('edit_student/<str:student_id>', HodViews.edit_student,name="edit_student"),
    path('edit_student_save', HodViews.edit_student_save,name="edit_student_save"),
    path('edit_matiere/<str:matiere_id>', HodViews.edit_matiere,name="edit_matiere"),
    path('edit_matiere_save', HodViews.edit_matiere_save,name="edit_matiere_save"),
    path('edit_classe/<str:classe_id>', HodViews.edit_classe,name="edit_classe"),
    path('add_matiere_classe/<str:classe_id>', HodViews.add_matiere_classe,name="add_matiere_classe"),
    path('edit_classe_save', HodViews.edit_classe_save,name="edit_classe_save"),
    path('manage_session', HodViews.manage_session,name="manage_session"),
    path('add_session_save', HodViews.add_session_save,name="add_session_save"),
    path('check_email_exist', HodViews.check_email_exist,name="check_email_exist"),
    path('check_username_exist', HodViews.check_username_exist,name="check_username_exist"),
    path('student_feedback_message', HodViews.student_feedback_message,name="student_feedback_message"),
    path('student_feedback_message_replied', HodViews.student_feedback_message_replied,name="student_feedback_message_replied"),
    path('professeur_feedback_message', HodViews.professeur_feedback_message,name="professeur_feedback_message"),
    path('professeur_feedback_message_replied', HodViews.professeur_feedback_message_replied,name="professeur_feedback_message_replied"),
    path('student_leave_view', HodViews.student_leave_view,name="student_leave_view"),
    path('professeur_leave_view', HodViews.professeur_leave_view,name="professeur_leave_view"),
    path('student_approve_leave/<str:leave_id>', HodViews.student_approve_leave,name="student_approve_leave"),
    path('student_disapprove_leave/<str:leave_id>', HodViews.student_disapprove_leave,name="student_disapprove_leave"),
    path('professeur_disapprove_leave/<str:leave_id>', HodViews.professeur_disapprove_leave,name="professeur_disapprove_leave"),
    path('professeur_approve_leave/<str:leave_id>', HodViews.professeur_approve_leave,name="professeur_approve_leave"),
    path('admin_view_attendance', HodViews.admin_view_attendance,name="admin_view_attendance"),
    path('admin_get_attendance_dates', HodViews.admin_get_attendance_dates,name="admin_get_attendance_dates"),
    path('admin_get_attendance_student', HodViews.admin_get_attendance_student,name="admin_get_attendance_student"),
    path('admin_profile', HodViews.admin_profile,name="admin_profile"),
    path('admin_profile_save', HodViews.admin_profile_save,name="admin_profile_save"),
    path('admin_send_notification_professeur', HodViews.admin_send_notification_professeur,name="admin_send_notification_professeur"),
    path('admin_send_notification_student', HodViews.admin_send_notification_student,name="admin_send_notification_student"),
    path('send_student_notification', HodViews.send_student_notification,name="send_student_notification"),
    path('send_professeur_notification', HodViews.send_professeur_notification,name="send_professeur_notification"),
    
    path('list-classes/<int:classe_id>/', HodViews.showClasse, name='show-classe'),
    path('voir_classes', HodViews.voirClasses,name="voirClasses"),
    
    path('delete_student/<int:student_id>/', HodViews.delete_student, name='delete_student'),
    
    
    path('liste-eleve-classe-generate-pdf/<int:classe_id>/', HodViews.list_eleve_classe_generate_pdf, name='list_eleve_classe_generate_pdf'),
    path('liste-eleve-classe-notes-pdf/<int:classe_id>/', HodViews.list_de_note_classe, name='list_eleve_classe_note_pdf'),
    

                  #     Professeur URL Path
    path('professeur_home', ProfesseurViews.professeur_home, name="professeur_home"),
    path('professeur_take_attendance', ProfesseurViews.professeur_take_attendance, name="professeur_take_attendance"),
    path('professeur_update_attendance', ProfesseurViews.professeur_update_attendance, name="professeur_update_attendance"),
    path('get_students', ProfesseurViews.get_students, name="get_students"),
    path('get_attendance_dates', ProfesseurViews.get_attendance_dates, name="get_attendance_dates"),
    path('get_attendance_student', ProfesseurViews.get_attendance_student, name="get_attendance_student"),
    path('save_attendance_data', ProfesseurViews.save_attendance_data, name="save_attendance_data"),
    path('save_updateattendance_data', ProfesseurViews.save_updateattendance_data, name="save_updateattendance_data"),
    path('professeur_apply_leave', ProfesseurViews.professeur_apply_leave, name="professeur_apply_leave"),
    path('professeur_apply_leave_save', ProfesseurViews.professeur_apply_leave_save, name="professeur_apply_leave_save"),
    path('professeur_feedback', ProfesseurViews.professeur_feedback, name="professeur_feedback"),
    path('professeur_feedback_save', ProfesseurViews.professeur_feedback_save, name="professeur_feedback_save"),
    path('professeur_profile', ProfesseurViews.professeur_profile, name="professeur_profile"),
    path('professeur_profile_save', ProfesseurViews.professeur_profile_save, name="professeur_profile_save"),
    path('professeur_fcmtoken_save', ProfesseurViews.professeur_fcmtoken_save, name="professeur_fcmtoken_save"),
    path('professeur_all_notification', ProfesseurViews.professeur_all_notification, name="professeur_all_notification"),
    path('professeur_add_result', ProfesseurViews.professeur_add_result, name="professeur_add_result"),
    path('save_student_result', ProfesseurViews.save_student_result, name="save_student_result"),
    path('edit_student_result',EditResultViewClass.as_view(), name="edit_student_result"),
    path('fetch_result_student',ProfesseurViews.fetch_result_student, name="fetch_result_student"),
    path('start_live_classroom',ProfesseurViews.start_live_classroom, name="start_live_classroom"),
    path('start_live_classroom_process',ProfesseurViews.start_live_classroom_process, name="start_live_classroom_process"),


    path('student_home', StudentViews.student_home, name="student_home"),
    path('student_view_attendance', StudentViews.student_view_attendance, name="student_view_attendance"),
    path('student_view_attendance_post', StudentViews.student_view_attendance_post, name="student_view_attendance_post"),
    path('student_apply_leave', StudentViews.student_apply_leave, name="student_apply_leave"),
    path('student_apply_leave_save', StudentViews.student_apply_leave_save, name="student_apply_leave_save"),
    path('student_feedback', StudentViews.student_feedback, name="student_feedback"),
    path('student_feedback_save', StudentViews.student_feedback_save, name="student_feedback_save"),
    path('student_profile', StudentViews.student_profile, name="student_profile"),
    path('student_profile_save', StudentViews.student_profile_save, name="student_profile_save"),
    path('student_fcmtoken_save', StudentViews.student_fcmtoken_save, name="student_fcmtoken_save"),
    path('firebase-messaging-sw.js',views.showFirebaseJS,name="show_firebase_js"),
    path('student_all_notification',StudentViews.student_all_notification,name="student_all_notification"),
    path('student_view_result',StudentViews.student_view_result,name="student_view_result"),
    path('join_class_room/<int:matiere_id>/<int:session_year_id>',StudentViews.join_class_room,name="join_class_room"),
    path('node_modules/canvas-designer/widget.html',ProfesseurViews.returnHtmlWidget,name="returnHtmlWidget"),
    path('testurl/',views.Testurl)
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
