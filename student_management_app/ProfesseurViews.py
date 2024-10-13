import json
from datetime import datetime
from uuid import uuid4

from django.contrib import messages
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from student_management_app.models import Matieres, SessionYearModel, Students, Attendance, AttendanceReport, \
    LeaveReportProfesseur, Professeurs, FeedBackProfesseurs, CustomUser, Classes, NotificationProfesseurs, StudentResult, OnlineClassRoom


def professeur_home(request):
    #For Fetch All Student Under Professeur
    matieres=Matieres.objects.filter(professeur_id=request.user.id)
    classe_id_list=[]
    for matiere in matieres:
        classe=Classes.objects.get(id=matiere.classe_id.id)
        classe_id_list.append(classe.id)

    final_classe=[]
    #removing Duplicate Classe ID
    for classe_id in classe_id_list:
        if classe_id not in final_classe:
            final_classe.append(classe_id)

    students_count=Students.objects.filter(classe_id__in=final_classe).count()

    #Fetch All Attendance Count
    attendance_count=Attendance.objects.filter(matiere_id__in=matieres).count()

    #Fetch All Approve Leave
    professeur=Professeurs.objects.get(admin=request.user.id)
    leave_count=LeaveReportProfesseur.objects.filter(professeur_id=professeur.id,leave_status=1).count()
    matiere_count=matieres.count()

    #Fetch Attendance Data by Matiere
    matiere_list=[]
    attendance_list=[]
    for matiere in matieres:
        attendance_count1=Attendance.objects.filter(matiere_id=matiere.id).count()
        matiere_list.append(matiere.matiere_name)
        attendance_list.append(attendance_count1)

    students_attendance=Students.objects.filter(classe_id__in=final_classe)
    student_list=[]
    student_list_attendance_present=[]
    student_list_attendance_absent=[]
    for student in students_attendance:
        attendance_present_count=AttendanceReport.objects.filter(status=True,student_id=student.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(status=False,student_id=student.id).count()
        student_list.append(student.admin.username)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    return render(request,"professeur_template/professeur_home_template.html",{"students_count":students_count,"attendance_count":attendance_count,"leave_count":leave_count,"matiere_count":matiere_count,"matiere_list":matiere_list,"attendance_list":attendance_list,"student_list":student_list,"present_list":student_list_attendance_present,"absent_list":student_list_attendance_absent})

def professeur_take_attendance(request):
    matieres=Matieres.objects.filter(professeur_id=request.user.id)
    session_years=SessionYearModel.objects.all()
    return render(request,"professeur_template/professeur_take_attendance.html",{"matieres":matieres,"session_years":session_years})

@csrf_exempt
def get_students(request):
    matiere_id=request.POST.get("matiere")
    session_year=request.POST.get("session_year")

    matiere=Matieres.objects.get(id=matiere_id)
    session_model=SessionYearModel.objects.get(id=session_year)
    students=Students.objects.filter(classe_id=matiere.classe_id,session_year_id=session_model)
    list_data=[]

    for student in students:
        data_small={"id":student.admin.id,"name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_attendance_data(request):
    student_ids=request.POST.get("student_ids")
    matiere_id=request.POST.get("matiere_id")
    attendance_date=request.POST.get("attendance_date")
    session_year_id=request.POST.get("session_year_id")

    matiere_model=Matieres.objects.get(id=matiere_id)
    session_model=SessionYearModel.objects.get(id=session_year_id)
    json_sstudent=json.loads(student_ids)
    #print(data[0]['id'])


    try:
        attendance=Attendance(matiere_id=matiere_model,attendance_date=attendance_date,session_year_id=session_model)
        attendance.save()

        for stud in json_sstudent:
             student=Students.objects.get(admin=stud['id'])
             attendance_report=AttendanceReport(student_id=student,attendance_id=attendance,status=stud['status'])
             attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")

def professeur_update_attendance(request):
    matieres=Matieres.objects.filter(professeur_id=request.user.id)
    session_year_id=SessionYearModel.objects.all()
    return render(request,"professeur_template/professeur_update_attendance.html",{"matieres":matieres,"session_year_id":session_year_id})

@csrf_exempt
def get_attendance_dates(request):
    matiere=request.POST.get("matiere")
    session_year_id=request.POST.get("session_year_id")
    matiere_obj=Matieres.objects.get(id=matiere)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)
    attendance=Attendance.objects.filter(matiere_id=matiere_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)

@csrf_exempt
def get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_updateattendance_data(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    json_sstudent=json.loads(student_ids)


    try:
        for stud in json_sstudent:
             student=Students.objects.get(admin=stud['id'])
             attendance_report=AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
             attendance_report.status=stud['status']
             attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")

def professeur_apply_leave(request):
    professeur_obj = Professeurs.objects.get(admin=request.user.id)
    leave_data=LeaveReportProfesseur.objects.filter(professeur_id=professeur_obj)
    return render(request,"professeur_template/professeur_apply_leave.html",{"leave_data":leave_data})

def professeur_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("professeur_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        professeur_obj=Professeurs.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportProfesseur(professeur_id=professeur_obj,leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("professeur_apply_leave"))
        except:
            messages.error(request, "Failed To Apply for Leave")
            return HttpResponseRedirect(reverse("professeur_apply_leave"))


def professeur_feedback(request):
    professeur_id=Professeurs.objects.get(admin=request.user.id)
    feedback_data=FeedBackProfesseurs.objects.filter(professeur_id=professeur_id)
    return render(request,"professeur_template/professeur_feedback.html",{"feedback_data":feedback_data})

def professeur_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("professeur_feedback_save"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        professeur_obj=Professeurs.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackProfesseurs(professeur_id=professeur_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("professeur_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("professeur_feedback"))

def professeur_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    professeur=Professeurs.objects.get(admin=user)
    return render(request,"professeur_template/professeur_profile.html",{"user":user,"professeur":professeur})

def professeur_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("professeur_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        address=request.POST.get("address")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            professeur=Professeurs.objects.get(admin=customuser.id)
            professeur.address=address
            professeur.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("professeur_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("professeur_profile"))

@csrf_exempt
def professeur_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        professeur=Professeurs.objects.get(admin=request.user.id)
        professeur.fcm_token=token
        professeur.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def professeur_all_notification(request):
    professeur=Professeurs.objects.get(admin=request.user.id)
    notifications=NotificationProfesseurs.objects.filter(professeur_id=professeur.id)
    return render(request,"professeur_template/all_notification.html",{"notifications":notifications})

def professeur_add_result(request):
    matieres=Matieres.objects.filter(professeur_id=request.user.id)
    session_years=SessionYearModel.objects.all()
    return render(request,"professeur_template/professeur_add_result.html",{"matieres":matieres,"session_years":session_years})

def save_student_result(request):
    if request.method!='POST':
        return HttpResponseRedirect('professeur_add_result')
    student_admin_id=request.POST.get('student_list')
    assignment_marks=request.POST.get('assignment_marks')
    exam_marks=request.POST.get('exam_marks')
    matiere_id=request.POST.get('matiere')


    student_obj=Students.objects.get(admin=student_admin_id)
    matiere_obj=Matieres.objects.get(id=matiere_id)

    try:
        check_exist=StudentResult.objects.filter(matiere_id=matiere_obj,student_id=student_obj).exists()
        if check_exist:
            result=StudentResult.objects.get(matiere_id=matiere_obj,student_id=student_obj)
            result.matiere_assignment_marks=assignment_marks
            result.matiere_exam_marks=exam_marks
            result.save()
            messages.success(request, "Successfully Updated Result")
            return HttpResponseRedirect(reverse("professeur_add_result"))
        else:
            result=StudentResult(student_id=student_obj,matiere_id=matiere_obj,matiere_exam_marks=exam_marks,matiere_assignment_marks=assignment_marks)
            result.save()
            messages.success(request, "Successfully Added Result")
            return HttpResponseRedirect(reverse("professeur_add_result"))
    except:
        messages.error(request, "Failed to Add Result")
        return HttpResponseRedirect(reverse("professeur_add_result"))

@csrf_exempt
def fetch_result_student(request):
    matiere_id=request.POST.get('matiere_id')
    student_id=request.POST.get('student_id')
    student_obj=Students.objects.get(admin=student_id)
    result=StudentResult.objects.filter(student_id=student_obj.id,matiere_id=matiere_id).exists()
    if result:
        result=StudentResult.objects.get(student_id=student_obj.id,matiere_id=matiere_id)
        result_data={"exam_marks":result.matiere_exam_marks,"assign_marks":result.matiere_assignment_marks}
        return HttpResponse(json.dumps(result_data))
    else:
        return HttpResponse("False")

def start_live_classroom(request):
    matieres=Matieres.objects.filter(professeur_id=request.user.id)
    session_years=SessionYearModel.objects.all()
    return render(request,"professeur_template/start_live_classroom.html",{"matieres":matieres,"session_years":session_years})

def start_live_classroom_process(request):
    session_year=request.POST.get("session_year")
    matiere=request.POST.get("matiere")

    matiere_obj=Matieres.objects.get(id=matiere)
    session_obj=SessionYearModel.objects.get(id=session_year)
    checks=OnlineClassRoom.objects.filter(matiere=matiere_obj,session_years=session_obj,is_active=True).exists()
    if checks:
        data=OnlineClassRoom.objects.get(matiere=matiere_obj,session_years=session_obj,is_active=True)
        room_pwd=data.room_pwd
        roomname=data.room_name
    else:
        room_pwd=datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
        roomname=datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
        professeur_obj=Professeurs.objects.get(admin=request.user.id)
        onlineClass=OnlineClassRoom(room_name=roomname,room_pwd=room_pwd,matiere=matiere_obj,session_years=session_obj,started_by=professeur_obj,is_active=True)
        onlineClass.save()

    return render(request,"professeur_template/live_class_room_start.html",{"username":request.user.username,"password":room_pwd,"roomid":roomname,"matiere":matiere_obj.matiere_name,"session_year":session_obj})


def returnHtmlWidget(request):
    return render(request,"widget.html")