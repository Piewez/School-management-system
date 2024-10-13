from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from student_management_app.forms import EditResultForm
from student_management_app.models import Students, Matieres, StudentResult


class EditResultViewClass(View):
    def get(self,request,*args,**kwargs):
        professeur_id=request.user.id
        edit_result_form=EditResultForm(professeur_id=professeur_id)
        return render(request,"professeur_template/edit_student_result.html",{"form":edit_result_form})

    def post(self,request,*args,**kwargs):
        form=EditResultForm(professeur_id=request.user.id,data=request.POST)
        if form.is_valid():
            student_admin_id = form.cleaned_data['student_ids']
            assignment_marks = form.cleaned_data['assignment_marks']
            exam_marks = form.cleaned_data['exam_marks']
            matiere_id = form.cleaned_data['matiere_id']

            student_obj = Students.objects.get(admin=student_admin_id)
            matiere_obj = Matieres.objects.get(id=matiere_id)
            result=StudentResult.objects.get(matiere_id=matiere_obj,student_id=student_obj)
            result.matiere_assignment_marks=assignment_marks
            result.matiere_exam_marks=exam_marks
            result.save()
            messages.success(request, "Successfully Updated Result")
            return HttpResponseRedirect(reverse("edit_student_result"))
        else:
            messages.error(request, "Failed to Update Result")
            form=EditResultForm(request.POST,professeur_id=request.user.id)
            return render(request,"professeur_template/edit_student_result.html",{"form":form})


