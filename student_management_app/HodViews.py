import json

import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg, Max, Min, Q
from django.db.models import OuterRef, Subquery, Exists, Value
from django.db.models.functions import Coalesce, Cast
from django.db.models import IntegerField, DecimalField, CharField, DateField, PositiveIntegerField
from decimal import Decimal
from django.conf import settings
from django.core.files.storage import default_storage
import os

from student_management_app.forms import AddStudentForm, EditStudentForm, AddPeriodeForm, EditPeriodeForm, AddExamenBlancForm
from student_management_app.models import CustomUser, Professeurs, Classes, Matieres, Students, SessionYearModel, \
    FeedBackStudent, FeedBackProfesseurs, LeaveReportStudent, LeaveReportProfesseur, Attendance, AttendanceReport, \
    NotificationStudent, NotificationProfesseurs, Periode, CategorieMatiere, Note, RangMatiere, Moyenne, MoyenneAnnuelle, \
        Bulletin, Comportement, ExamenBlanc, NumeroTableExamen, ExamenNote, MoyenneExamen, Economes, Secretaire, Surveillant
            

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from io import BytesIO
from reportlab.pdfgen import canvas
from operator import attrgetter
from django.db.models.functions import DenseRank, RowNumber
import zipfile
from django.db.models import F, Window
import datetime
from reportlab.lib.utils import ImageReader
from django.db.models import F, Sum, ExpressionWrapper, Case, When
from django.template.loader import get_template

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


import qrcode
from django.core.files import File

import decimal


from django.contrib.staticfiles import finders

school_name = "LYCEE DE SOTUBOUA"

def admin_home(request):
    student_count1=Students.objects.all().count()
    professeur_count=Professeurs.objects.all().count()
    matiere_count=Matieres.objects.all().count()
    classe_count=Classes.objects.all().count()

    classe_all=Classes.objects.all()
    classe_name_list=[]
    matiere_count_list=[]
    student_count_list_in_classe=[]
    for classe in classe_all:
        matieres=Matieres.objects.filter(classe_id=classe.id).count()
        students=Students.objects.filter(classe_id=classe.id).count()
        classe_name_list.append(classe.classe_name)
        matiere_count_list.append(matieres)
        student_count_list_in_classe.append(students)

    matieres_all=Matieres.objects.all()
    matiere_list=[]
    student_count_list_in_matiere=[]
    for matiere in matieres_all:
        classe=Classes.objects.get(id=matiere.classe_id.id)
        student_count=Students.objects.filter(classe_id=classe.id).count()
        matiere_list.append(matiere.matiere_name)
        student_count_list_in_matiere.append(student_count)

    professeurs=Professeurs.objects.all()
    attendance_present_list_professeur=[]
    attendance_absent_list_professeur=[]
    professeur_name_list=[]
    for professeur in professeurs:
        matiere_ids=Matieres.objects.filter(professeur_id=professeur.admin.id)
        attendance=Attendance.objects.filter(matiere_id__in=matiere_ids).count()
        leaves=LeaveReportProfesseur.objects.filter(professeur_id=professeur.id,leave_status=1).count()
        attendance_present_list_professeur.append(attendance)
        attendance_absent_list_professeur.append(leaves)
        professeur_name_list.append(professeur.admin.username)

    students_all=Students.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        leaves=LeaveReportStudent.objects.filter(student_id=student.id,leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves+absent)
        student_name_list.append(student.admin.username)


    return render(request,"hod_template/home_content.html",{"student_count":student_count1,"professeur_count":professeur_count,"matiere_count":matiere_count,"classe_count":classe_count,"classe_name_list":classe_name_list,"matiere_count_list":matiere_count_list,"student_count_list_in_classe":student_count_list_in_classe,"student_count_list_in_matiere":student_count_list_in_matiere,"matiere_list":matiere_list,"professeur_name_list":professeur_name_list,"attendance_present_list_professeur":attendance_present_list_professeur,"attendance_absent_list_professeur":attendance_absent_list_professeur,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student})


def add_anneescolaire(request):
    return render(request,"hod_template/add_annneescolaire_template.html")

def add_anneescolaire_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("add_anneescolaire"))
    else:
        anneescolaire=request.POST.get("anneescolaire")
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")
        is_complete=request.POST.get("is_complete")
        
        if is_complete == 'on':
            is_complete = True
        else:
            is_complete = False

        try:
            sessionyear=SessionYearModel(nom=anneescolaire,session_start_year=session_start_year,session_end_year=session_end_year,is_complete=is_complete)
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("add_anneescolaire"))
        except Exception as e:
            messages.error(request, f"Failed to Add Session: {str(e)}")
            return HttpResponseRedirect(reverse("add_anneescolaire"))
        

def add_periode(request):
    form=AddPeriodeForm()
    return render(request,"hod_template/add_periode_template.html",{"form":form})

def add_periode_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddPeriodeForm(request.POST)
        if form.is_valid():
            periode_name=form.cleaned_data["nom"]
            session_year_id=form.cleaned_data["annee_scolaire"]


            try:
                periode=Periode(periode_name=periode_name)
                session_year=SessionYearModel.objects.get(id=session_year_id)
                periode.annee_scolaire=session_year
                periode.save()
                messages.success(request,"Successfully Added Periode")
                return HttpResponseRedirect(reverse("add_periode"))
            except Exception as e:
                messages.error(request,f"Failed to Add Periode: {str(e)}")
                return HttpResponseRedirect(reverse("add_periode"))
        else:
            form=AddPeriodeForm(request.POST)
            return render(request, "hod_template/add_periode_template.html", {"form": form})



def add_examen_blanc(request):
    if request.method == 'POST':
        form = AddExamenBlancForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            annee_scolaire_id = form.cleaned_data['annee_scolaire']
            classes_ids = form.cleaned_data['classes_concernees']
            
            # Récupérer l'année scolaire sélectionnée
            annee_scolaire = SessionYearModel.objects.get(id=annee_scolaire_id)
            
            # Créer l'examen blanc
            examen_blanc = ExamenBlanc.objects.create(
                nom=nom,
                annee_scolaire=annee_scolaire
            )
            
            # Ajouter les classes concernées
            examen_blanc.classes_concernees.set(Classes.objects.filter(id__in=classes_ids))
            
            # Appeler la méthode pour assigner les numéros de table
            examen_blanc.assigner_numero_table()
            
            return redirect('admin_home')  # Rediriger après la création
    else:
        form = AddExamenBlancForm()

    return render(request, 'hod_template/add_examen_blanc_template.html', {'form': form})


def afficher_eleves_concernes1(request, examen_blanc_id):
    # Récupérer l'examen blanc
    examen_blanc = get_object_or_404(ExamenBlanc, id=examen_blanc_id)
    
    # Récupérer les élèves des classes concernées par cet examen
    eleves_concernes = Students.objects.filter(classe_id__in=examen_blanc.classes_concernees.all()).order_by('admin__first_name', 'admin__last_name')

    # Rendre les données dans le template
    return render(request, 'hod_template/afficher_eleves_concernes_examen.html', {
        'examen_blanc': examen_blanc,
        'eleves_concernes': eleves_concernes
    })
    


def afficher_eleves_concernes(request, examen_blanc_id):
    # Récupérer l'examen blanc
    examen_blanc = get_object_or_404(ExamenBlanc, id=examen_blanc_id)
    
    # Récupérer les élèves des classes concernées par cet examen
    eleves_concernes = Students.objects.filter(classe_id__in=examen_blanc.classes_concernees.all()).order_by('admin__first_name', 'admin__last_name')

    # Récupérer les numéros de table pour chaque élève
    numeros_table = {}
    for eleve in eleves_concernes:
        try:
            numero_table = NumeroTableExamen.objects.get(examen_blanc=examen_blanc, student=eleve)
            numeros_table[eleve.id] = numero_table.numero_table
        except NumeroTableExamen.DoesNotExist:
            numeros_table[eleve.id] = None
    
    numero_table_eleves = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc)
    for numero_table_eleve in numero_table_eleves:
        print(numero_table_eleve.numero_table)
    # Rendre les données dans le template
    return render(request, 'hod_template/view_examen_students.html', {
        'examen_blanc': examen_blanc,
        'eleves_concernes': eleves_concernes,
        'numeros_table': numeros_table,
        'numero_table_eleves':numero_table_eleves,
    })


def list_eleve_examen_generate_pdf(request, examen_blanc_id):
    # Récupérer l'examen blanc
    examen_blanc = get_object_or_404(ExamenBlanc, id=examen_blanc_id)
    
    # Récupérer les élèves des classes concernées par cet examen
    eleves_concernes = Students.objects.filter(classe_id__in=examen_blanc.classes_concernees.all()).order_by('admin__first_name', 'admin__last_name')

    # Récupérer les numéros de table pour chaque élève
    numeros_table = {}
    for eleve in eleves_concernes:
        try:
            numero_table = NumeroTableExamen.objects.get(examen_blanc=examen_blanc, student=eleve)
            numeros_table[eleve.id] = numero_table.numero_table
        except NumeroTableExamen.DoesNotExist:
            numeros_table[eleve.id] = None
    
    numero_table_eleves = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc)

    # Créer un objet BytesIO pour stocker le PDF
    buffer = BytesIO()

    # Créer un SimpleDocTemplate pour gérer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Créer un tableau pour les données des élèves
    col_widths = [100, 150, 150, 50, 100]
    table_data = [['N° de Table', 'NOM', 'PRENOM', 'SEXE', 'Date de Nais']] + \
                 [[numero_table_eleve.numero_table, numero_table_eleve.student.admin.first_name, numero_table_eleve.student.admin.last_name, numero_table_eleve.student.gender, numero_table_eleve.student.date_naissance] for numero_table_eleve in numero_table_eleves]
    table = Table(table_data, colWidths=col_widths, rowHeights=None)

    # Appliquer un style au tableau
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    elements = []
    
    heading_style = getSampleStyleSheet()['Heading2']
    heading_style.alignment = 1  # 0=Left, 1=Center, 2=Right
    elements.append(Paragraph(school_name, heading_style))
    elements.append(Paragraph("Liste des élèves du " + examen_blanc.nom, getSampleStyleSheet()['Heading1']))
    elements.append(table)
    

    # Générer le PDF
    doc.build(elements)

    # Récupérer le contenu du buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Retourner le PDF en tant que réponse HTTP pour le téléchargement ou l'affichage
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Liste des eleves du {examen_blanc.nom}.pdf"'
    response.write(pdf)
    return response


def add_professeur(request):
    return render(request,"hod_template/add_professeur_template.html")

def add_professeur_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=2)
            user.professeurs.address=address
            user.save()
            messages.success(request,"Successfully Added Professeur")
            return HttpResponseRedirect(reverse("add_professeur"))
        except Exception as e:
            messages.error(request,f"Failed to Add Professeur: {str(e)}")
            return HttpResponseRedirect(reverse("add_professeur"))
        
def add_econome(request):
    return render(request,"hod_template/add_econome_template.html")

def add_econome_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=4)
            user.economes.address=address
            user.save()
            messages.success(request,"Successfully Added econome")
            return HttpResponseRedirect(reverse("add_econome"))
        except Exception as e:
            messages.error(request,f"Failed to Add econome: {str(e)}")
            return HttpResponseRedirect(reverse("add_econome"))
       
def add_classe(request):
    professeurs=Professeurs.objects.all()
    return render(request,"hod_template/add_classe_template.html",{"professeurs":professeurs})

def add_classe_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        classe=request.POST.get("classe")
        professeur_id=request.POST.get("professeur")
        professeur=Professeurs.objects.get(id=professeur_id)
        try:
            classe_model=Classes(classe_name=classe, titulaire=professeur)
            classe_model.save()
            messages.success(request,"Successfully Added Classe")
            return HttpResponseRedirect(reverse("add_classe"))
        except Exception as e:
            print(e)
            messages.error(request,f"Failed To Add Classe : {str(e)}")
            return HttpResponseRedirect(reverse("add_classe"))
        
def add_categorie_matiere(request):
    return render(request,"hod_template/add_categorie_matiere_template.html")

def add_categorie_matiere_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        categorie_matiere=request.POST.get("categorie_matiere")
        try:
            categorie_matiere_model=CategorieMatiere(nom=categorie_matiere)
            categorie_matiere_model.save()
            messages.success(request,"Catégorie de la matière est ajouté avec succès")
            return HttpResponseRedirect(reverse("add_categorie_matiere"))
        except Exception as e:
            print(e)
            messages.error(request,f"Echec d'ajout de la catégorie : {str(e)}")
            return HttpResponseRedirect(reverse("add_categorie_matiere"))
        
def add_student(request):
    form = AddStudentForm()
    return render(request, "hod_template/add_student_template.html", {"form": form})

def add_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        form = AddStudentForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"] or "piro1234"  # Mot de passe par défaut si non fourni
            address = form.cleaned_data["address"]
            numero_matricule = form.cleaned_data["numero_matricule"]
            statut = form.cleaned_data["statut"]
            contact_parent = form.cleaned_data["contact_parent"]
            annee_scolaire = form.cleaned_data["annee_scolaire"]
            date_naissance = form.cleaned_data["date_naissance"]
            aptitude_sport = form.cleaned_data["aptitude_sport"]
            classe_id = form.cleaned_data["classe"]
            sex = form.cleaned_data["sex"]

            # Photo de profil facultative
            if 'profile_pic' in request.FILES:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = ""  # Ou utiliser une image par défaut

            try:
                user = CustomUser.objects.create_user(
                    username=email,  # Utiliser l'email comme username
                    password=password,
                    email=email,
                    last_name=last_name,
                    first_name=first_name,
                    user_type=3
                )
                
                user.students.address = address
                classe_obj = Classes.objects.get(id=classe_id)
                user.students.classe_id = classe_obj
                annee_scolaire = SessionYearModel.objects.get(id=annee_scolaire)
                user.students.annee_scolaire = annee_scolaire
                user.students.gender = sex
                user.students.numero_matricule = numero_matricule
                user.students.statut = statut
                user.students.contact_parent = contact_parent
                user.students.date_naissance = date_naissance
                user.students.aptitude_sport = aptitude_sport
                user.students.profile_pic = profile_pic_url
                user.save()
                
                messages.success(request, "Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))
            except Exception as e:
                error_message = f"Failed to Add Student: {str(e)}"
                print(error_message)  # Pour le débogage
                messages.error(request, error_message)
                return HttpResponseRedirect(reverse("add_student"))
        else:
            return render(request, "hod_template/add_student_template.html", {"form": form})


def add_matiere(request):
    classes=Classes.objects.all()
    professeurs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/add_matiere_template.html",{"professeurs":professeurs,"classes":classes})

def add_matiere_classe(request, classe_id):
    classe=Classes.objects.get(id=classe_id)
    professeurs=Professeurs.objects.all()
    categories=CategorieMatiere.objects.all()
    return render(request,"hod_template/add_matiere_classe_template.html",{"professeurs":professeurs,"classe":classe,"categories":categories})

def add_matiere_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        matiere_name=request.POST.get("matiere_name")
        classe_id=request.POST.get("classe")
        coefficient=request.POST.get("coefficient")
        categorie_id=request.POST.get("categorie")
        categorie=CategorieMatiere.objects.get(id=categorie_id)
        classe=Classes.objects.get(id=classe_id)
        professeur_id=request.POST.get("professeur")
        professeur=Professeurs.objects.get(id=professeur_id)

        try:
            matiere=Matieres(matiere_name=matiere_name,classe_id=classe,professeur_id=professeur,categorie=categorie,coefficient=coefficient)
            matiere.save()
            messages.success(request,"Successfully Added Matiere")
            return HttpResponseRedirect(reverse("voirClasses"))
        except Exception as e:
            messages.error(request,f"Failed to Add Matiere: {str(e)}")
            return HttpResponseRedirect(reverse("voirClasses"))


def manage_professeur(request):
    context = {"professeurs": Professeurs.objects.all().order_by("admin__first_name"),
               }
    return render(request,"hod_template/manage_professeur_template.html",context)

def manage_econome(request):
    context = {"economes": Economes.objects.all().order_by("admin__first_name"),
               }
    return render(request,"hod_template/manage_econome_template.html",context)

def manage_student(request):
    annee_scolaire_id = request.GET.get('annee_scolaire', None)
    
    if annee_scolaire_id:
        annee_scolaire = get_object_or_404(SessionYearModel, pk=annee_scolaire_id)
    else:
        annee_scolaire = SessionYearModel.objects.filter(is_complete=False).first()

    students = Students.objects.filter(annee_scolaire=annee_scolaire).order_by('admin__first_name')
    annees_scolaires = SessionYearModel.objects.all()
    classes_info = Classes.objects.annotate(nombre_eleves=Count('students')).select_related('titulaire__admin').order_by('classe_name')

    return render(request,"hod_template/manage_student_template.html",{
        "students":students,
        "classes_info":classes_info,
        
        'annees_scolaires': annees_scolaires,
        'annee_scolaire_selected': annee_scolaire,
        })


def manage_matiere1(request):
    matieres=Matieres.objects.all()
    return render(request,"hod_template/manage_matiere_template.html",{"matieres":matieres})

def manage_matiere_classe(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    matieres = Matieres.objects.filter(classe_id=classe).order_by('coefficient')
    return render(request,"hod_template/manage_matiere_classe_template.html",{"matieres":matieres,"classe":classe})

def manage_matiere(request):
    matieres=Matieres.objects.all()
    classes = Classes.objects.all()
    return render(request,"hod_template/manage_matiere_template.html",{"matieres":matieres,"classes":classes})

def manage_anneescolaire(request):
    anneescolaires=SessionYearModel.objects.all()
    return render(request,"hod_template/manage_anneescolaire_template.html",{"anneescolaires":anneescolaires})

def manage_periode(request):
    periodes=Periode.objects.all()
    return render(request,"hod_template/manage_periode_template.html",{"periodes":periodes})

def manage_examen(request):
    examens=ExamenBlanc.objects.all()
    return render(request,"hod_template/examens_template.html",{"examens":examens})

def choose_examen_to_add_note(request):
    annee_scolaire_id = request.GET.get('annee_scolaire', None)
    
    if annee_scolaire_id:
        annee_scolaire = get_object_or_404(SessionYearModel, pk=annee_scolaire_id)
    else:
        annee_scolaire = SessionYearModel.objects.filter(is_complete=False).first()

    annees_scolaires = SessionYearModel.objects.all()
    examens=ExamenBlanc.objects.filter(annee_scolaire=annee_scolaire)
    return render(request,"hod_template/choose_Examen_To_Add_Notes.html",{
        "examens":examens,
        'annees_scolaires': annees_scolaires,
        'annee_scolaire_selected': annee_scolaire,
        })
    
def choose_examen_to_view_note(request):
    annee_scolaire_id = request.GET.get('annee_scolaire', None)
    
    if annee_scolaire_id:
        annee_scolaire = get_object_or_404(SessionYearModel, pk=annee_scolaire_id)
    else:
        annee_scolaire = SessionYearModel.objects.filter(is_complete=False).first()

    annees_scolaires = SessionYearModel.objects.all()
    examens=ExamenBlanc.objects.filter(annee_scolaire=annee_scolaire)
    return render(request,"hod_template/choose_Examen_To_View_Notes.html",{
        "examens":examens,
        'annees_scolaires': annees_scolaires,
        'annee_scolaire_selected': annee_scolaire,
        })
    
def choose_examen_to_view_results(request):
    annee_scolaire_id = request.GET.get('annee_scolaire', None)
    
    if annee_scolaire_id:
        annee_scolaire = get_object_or_404(SessionYearModel, pk=annee_scolaire_id)
    else:
        annee_scolaire = SessionYearModel.objects.filter(is_complete=False).first()

    annees_scolaires = SessionYearModel.objects.all()
    examens=ExamenBlanc.objects.filter(annee_scolaire=annee_scolaire)
    return render(request,"hod_template/choose_Examen_To_View_Results.html",{
        "examens":examens,
        'annees_scolaires': annees_scolaires,
        'annee_scolaire_selected': annee_scolaire,
        })

def manage_categorie(request):
    categories=CategorieMatiere.objects.all()
    return render(request,"hod_template/manage_categorie_template.html",{"categories":categories})

def manage_classe(request):
    # Annotate the number of students and order by classe_name alphabetically
    classes_info = Classes.objects.annotate(nombre_eleves=Count('students')).select_related('titulaire__admin').order_by('classe_name')

    context = {
        'classes_info': classes_info,
    }
    return render(request, "hod_template/manage_classe_template.html", context)

def showClasse(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)

    # Récupérer l'année scolaire sélectionnée, sinon l'année en cours
    annee_scolaire_id = request.GET.get('annee_scolaire', None)
    
    
    
    if annee_scolaire_id:
        annee_scolaire = get_object_or_404(SessionYearModel, pk=annee_scolaire_id)
    else:
        annee_scolaire = SessionYearModel.objects.filter(is_complete=False).first()

    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire).order_by('admin__first_name')
    annees_scolaires = SessionYearModel.objects.all()
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)
    comportement = Comportement.objects.all()
    periode = Periode.objects.filter(annee_scolaire=SessionYearModel.get_current_session()).first()
    
    eleves_aspects = {}
    eleves_aspects_points = {}
    for eleve in eleves:
        aspects = eleve.comportements.all()
        eleves_aspects[eleve.admin.first_name] = [aspect.aspect for aspect in aspects]
        eleves_aspects_points[eleve.admin.first_name] = [aspect.points for aspect in aspects]
        
    for eleve, aspect in eleves_aspects.items():
        print(f'{eleve} : {aspect}')
    for eleve, aspect in eleves_aspects_points.items():
        print(f'{eleve} : {aspect}')
        
    
        
    return render(request, "hod_template/show-classe.html", {
        'classe': classe,
        'eleves': eleves,
        'annees_scolaires': annees_scolaires,
        'annee_scolaire_selected': annee_scolaire,
        'trimestres':trimestres,
    })

def voirClasses(request):
    classes = Classes.objects.all()
    return render(request,"hod_template/voir-classes.html",{"classes":classes})
def choose_Classe_To_Add_Notes(request):
    classes = Classes.objects.all()
    return render(request,"hod_template/choose_Classe_To_Add_Notes.html",{"classes":classes})
def choose_Classe_To_View_Notes(request):
    classes = Classes.objects.all()
    return render(request,"hod_template/choose_Classe_To_View_Notes.html",{"classes":classes})
def choose_Classe_To_View_Results(request):
    classes = Classes.objects.all()
    return render(request,"hod_template/choose_Classe_To_View_Results.html",{"classes":classes})

def delete_student(request, student_id):
    student = get_object_or_404(Students, pk=student_id)
    student.delete()
    messages.success(request, "L'élève a été supprimé avec succès.")
    return redirect('manage_classe')  # Redirige vers la vue qui liste les classes ou les élèves
def delete_professeur(request, professeur_id):
    professeur = get_object_or_404(Professeurs, pk=professeur_id)
    professeur.delete()
    messages.success(request, "Le professeur a été supprimé avec succès.")
    return redirect('manage_professeur')  # Redirige vers la vue qui liste les classes ou les élèves
def delete_econome(request, econome_id):
    econome = get_object_or_404(Economes, pk=econome_id)
    econome.delete()
    messages.success(request, "L'econome a été supprimé avec succès.")
    return redirect('manage_econeme')  # Redirige vers la vue qui liste les classes ou les élèves
def delete_classe(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    classe.delete()
    messages.success(request, "La classe a été supprimé avec succès.")
    return redirect('manage_classe')  # Redirige vers la vue qui liste les classes ou les élèves
def delete_matiere(request, matiere_id):
    matiere = get_object_or_404(Matieres, pk=matiere_id)
    matiere.delete()
    messages.success(request, "La matière a été supprimé avec succès.")
    return redirect('manage_matiere')  # Redirige vers la vue qui liste les classes ou les élèves
def delete_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    classe_id = note.eleve.classe_id.id 
    note.delete()
    messages.success(request, "La note a été supprimée avec succès.")
    return redirect('view_note', classe_id=classe_id)  # Remplacez par la vue appropriée


def edit_professeur(request, professeur_id):
    print(f"Received professeur_id: {professeur_id}")  # Debug
    try:
        professeur = Professeurs.objects.get(id=professeur_id)
        print(f"Found professeur: {professeur.id}")  # Debug
        return render(request, "hod_template/edit_professeur_template.html", {"professeur": professeur, "id": professeur.id})
    except Professeurs.DoesNotExist:
        print("Professeur not found!")  # Debug
        messages.error(request, "Le professeur spécifié n'existe pas.")
        return HttpResponseRedirect(reverse("manage_professeur"))

def edit_professeur_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        professeur_id = request.POST.get("professeur_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        address = request.POST.get("address")
        try:
            # Récupérer l'objet Professeur par ID
            professeur_model = Professeurs.objects.get(admin=professeur_id)
            # Récupérer l'utilisateur associé
            user = professeur_model.admin
            
            # Mettre à jour les informations de l'utilisateur
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            # Mettre à jour les informations du professeur
            professeur_model.address = address
            professeur_model.save()

            messages.success(request, "Successfully Edited Professeur")
            return HttpResponseRedirect(reverse("edit_professeur", kwargs={"professeur_id": professeur_id}))
        except Professeurs.DoesNotExist:
            messages.error(request, "Failed to Edit Professeur - Professeur not found")
            return HttpResponseRedirect(reverse("edit_professeur", kwargs={"professeur_id": professeur_id}))
        except CustomUser.DoesNotExist:
            messages.error(request, "Failed to Edit Professeur - User not found")
            return HttpResponseRedirect(reverse("edit_professeur", kwargs={"professeur_id": professeur_id}))
        except Exception as e:
            messages.error(request, f"Failed to Edit Professeur: {str(e)}")
            return HttpResponseRedirect(reverse("edit_professeur", kwargs={"professeur_id": professeur_id}))

def edit_student(request,student_id):
    request.session['student_id']=student_id
    student=Students.objects.get(id=student_id)
    form=EditStudentForm()
    form.fields['email'].initial=student.admin.email
    form.fields['first_name'].initial=student.admin.first_name
    form.fields['last_name'].initial=student.admin.last_name
    form.fields['username'].initial=student.admin.username
    form.fields['address'].initial=student.address
    form.fields['numero_matricule'].initial=student.numero_matricule
    form.fields['statut'].initial=student.statut
    form.fields['contact_parent'].initial=student.contact_parent
    form.fields['date_naissance'].initial=student.date_naissance
    form.fields['aptitude_sport'].initial=student.aptitude_sport
    form.fields['classe'].initial=student.classe_id.id
    form.fields['sex'].initial=student.gender
    form.fields['annee_scolaire'].initial=student.annee_scolaire.id
    return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

def edit_student_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id=request.session.get("student_id")
        if student_id==None:
            return HttpResponseRedirect(reverse("manage_student"))
        print(f'Student Id :{student_id}')
        form=EditStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            numero_matricule = form.cleaned_data["numero_matricule"]
            statut = form.cleaned_data["statut"]
            contact_parent = form.cleaned_data["contact_parent"]
            date_naissance = form.cleaned_data["date_naissance"]
            aptitude_sport = form.cleaned_data["aptitude_sport"]
            annee_scolaire=form.cleaned_data["annee_scolaire"]
            classe_id = form.cleaned_data["classe"]
            sex = form.cleaned_data["sex"]

            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None


            try:
                # Récupérer l'objet Student via son ID
                student = Students.objects.get(id=student_id)
                
                # Récupérer l'utilisateur associé via le champ 'admin'
                user = student.admin

                # Vérifiez si le nom d'utilisateur a changé
                if user.username != username:
                    # Vérifiez que le nouveau nom d'utilisateur n'est pas déjà pris
                    if CustomUser.objects.filter(username=username).exclude(id=user.id).exists():
                        raise Exception("Le nom d'utilisateur existe déjà.")
                    user.username = username  # Mettre à jour le nom d'utilisateur uniquement s'il est différent
                
                # Mettre à jour les autres champs de l'utilisateur
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()


                student=Students.objects.get(id=student_id)
                student.address=address
                student.numero_matricule=numero_matricule
                student.statut=statut
                student.contact_parent=contact_parent
                student.date_naissance=date_naissance
                student.aptitude_sport=aptitude_sport
                session_year = SessionYearModel.objects.get(id=annee_scolaire)
                student.annee_scolaire = session_year
                student.gender=sex
                classe=Classes.objects.get(id=classe_id)
                student.classe_id=classe
                if profile_pic_url!=None:
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request,"Successfully Edited Student")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
            except Exception as e:
                print(e)
                messages.error(request,f"Failed to Edit Student : {str(e)}")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
        else:
            form=EditStudentForm(request.POST)
            student=Students.objects.get(admin=student_id)
            return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

def edit_matiere(request,matiere_id):
    matiere=Matieres.objects.get(id=matiere_id)
    classes=Classes.objects.all()
    categories=CategorieMatiere.objects.all()
    professeurs=Professeurs.objects.all()
    return render(request,"hod_template/edit_matiere_template.html",{"matiere":matiere,"professeurs":professeurs,"classes":classes,"id":matiere_id,"categories":categories})

def edit_matiere_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        matiere_id=request.POST.get("matiere_id")
        matiere_name=request.POST.get("matiere_name")
        coefficient=request.POST.get("coefficient")
        categorie_matiere=request.POST.get("categorie")
        professeur_id=request.POST.get("professeur")
        classe_id=request.POST.get("classe")

        try:
            matiere=Matieres.objects.get(id=matiere_id)
            matiere.matiere_name=matiere_name
            matiere.coefficient=coefficient
            categorie_matiere=CategorieMatiere.objects.get(id=categorie_matiere)
            matiere.categorie=categorie_matiere
            professeur=Professeurs.objects.get(id=professeur_id)
            matiere.professeur_id=professeur
            classe=Classes.objects.get(id=classe_id)
            matiere.classe_id=classe
            matiere.save()

            messages.success(request,"Successfully Edited Matiere")
            return HttpResponseRedirect(reverse("edit_matiere",kwargs={"matiere_id":matiere_id}))
        except Exception as e:
            print(e)
            messages.error(request,"Failed to Edit Matiere")
            return HttpResponseRedirect(reverse("edit_matiere",kwargs={"matiere_id":matiere_id}))


def edit_anneescolaire(request,anneescolaire_id):
    anneescolaire=SessionYearModel.objects.get(id=anneescolaire_id)
    return render(request,"hod_template/edit_anneescolaire_template.html",{"anneescolaire":anneescolaire,"id":anneescolaire_id})

def edit_anneescolaire_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        anneescolaire_id=request.POST.get("anneescolaire_id")
        anneescolaire_name=request.POST.get("annneescolaire_name")
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")
        is_complete=request.POST.get("is_complete")
        
        if is_complete == 'on':
            is_complete = True
        else:
            is_complete = False


        try:
            anneescolaire=SessionYearModel.objects.get(id=anneescolaire_id)
            print(SessionYearModel.nom)
            
            anneescolaire.nom=anneescolaire_name
            anneescolaire.session_start_year=session_start_year
            anneescolaire.session_end_year=session_end_year
            anneescolaire.is_complete=is_complete
            anneescolaire.save()
            messages.success(request,"Successfully Edited Session Year")
            return HttpResponseRedirect(reverse("edit_anneescolaire",kwargs={"anneescolaire_id":anneescolaire_id}))
        except Exception as e:
            messages.error(request,f"Failed to Edit Session Year: {str(e)}")
            return HttpResponseRedirect(reverse("edit_anneescolaire",kwargs={"anneescolaire_id":anneescolaire_id}))


def edit_periode(request,periode_id):
    request.session['periode_id']=periode_id
    periode=Periode.objects.get(id=periode_id)
    form=EditPeriodeForm()
    form.fields['annee_scolaire'].initial=periode.annee_scolaire.id
    return render(request,"hod_template/edit_periode_template.html",{"form":form,"id":periode_id})

def edit_periode_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        periode_id=request.session.get("periode_id")
        if periode_id==None:
            return HttpResponseRedirect(reverse("manage_periode"))

        form=EditPeriodeForm(request.POST)
        if form.is_valid():
            periode_name = form.cleaned_data["nom"]
            session_year_id=form.cleaned_data["annee_scolaire"]


            try:

                periode=Periode.objects.get(id=periode_id)
                periode.periode_name=periode_name
                session_year=SessionYearModel.objects.get(id=session_year_id)
                periode.annee_scolaire=session_year
                periode.save()
                del request.session['periode_id']
                messages.success(request,"Successfully Edited Periode")
                return HttpResponseRedirect(reverse("edit_periode",kwargs={"periode_id":periode_id}))
            except Exception as e:
                messages.error(request,f"Failed to Edit Periode : {str(e)}")
                return HttpResponseRedirect(reverse("edit_periode",kwargs={"periode_id":periode_id}))
        else:
            form=EditPeriodeForm(request.POST)
            student=Students.objects.get(admin=periode_id)
            return render(request,"hod_template/edit_periode_template.html",{"form":form,"id":periode_id,"username":student.admin.username})


def edit_categorie_matiere(request,categorie_matiere_id):
    categorie_matiere=CategorieMatiere.objects.get(id=categorie_matiere_id)
    return render(request,"hod_template/edit_categorie_matiere_template.html",{"categorie_matiere":categorie_matiere,"id":categorie_matiere_id})

def edit_categorie_matiere_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        categorie_matiere_id=request.POST.get("categorie_matiere_id")
        categorie_name=request.POST.get("categorie_matiere_name")

        try:
            categorie=CategorieMatiere.objects.get(id=categorie_matiere_id)
            print(Classes.classe_name)
            categorie.nom=categorie_name
            categorie.save()
            messages.success(request,"Successfully Edited Catégorie")
            return HttpResponseRedirect(reverse("edit_categorie_matiere",kwargs={"categorie_matiere_id":categorie_matiere_id}))
        except Exception as e:
            messages.error(request,f"Failed to Edit Catégorie: {str(e)}")
            return HttpResponseRedirect(reverse("edit_categorie_matiere",kwargs={"categorie_matiere_id":categorie_matiere_id}))

def edit_classe(request,classe_id):
    classe=Classes.objects.get(id=classe_id)
    professeurs=Professeurs.objects.all()
    return render(request,"hod_template/edit_classe_template.html",{"classe":classe,"id":classe_id,"professeurs":professeurs})

def edit_classe_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        classe_id=request.POST.get("classe_id")
        classe_name=request.POST.get("classe")
        professeur_id=request.POST.get("titulaire")
        professeur=Professeurs.objects.get(id=professeur_id)

        try:
            classe=Classes.objects.get(id=classe_id)
            print(Classes.classe_name)
            classe.classe_name=classe_name
            classe.titulaire=professeur
            classe.save()
            messages.success(request,"Successfully Edited Classe")
            return HttpResponseRedirect(reverse("edit_classe",kwargs={"classe_id":classe_id}))
        except Exception as e:
            messages.error(request,f"Failed to Edit Classe: {str(e)}")
            return HttpResponseRedirect(reverse("edit_classe",kwargs={"classe_id":classe_id}))


def manage_session(request):
    return render(request,"hod_template/manage_session_template.html")

def add_session_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            sessionyear=SessionYearModel(session_start_year=session_start_year,session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect(reverse("manage_session"))

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def professeur_feedback_message(request):
    feedbacks=FeedBackProfesseurs.objects.all()
    return render(request,"hod_template/professeur_feedback_template.html",{"feedbacks":feedbacks})

def student_feedback_message(request):
    feedbacks=FeedBackStudent.objects.all()
    return render(request,"hod_template/student_feedback_template.html",{"feedbacks":feedbacks})

@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def professeur_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackProfesseurs.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def professeur_leave_view(request):
    leaves=LeaveReportProfesseur.objects.all()
    return render(request,"hod_template/professeur_leave_view.html",{"leaves":leaves})

def student_leave_view(request):
    leaves=LeaveReportStudent.objects.all()
    return render(request,"hod_template/student_leave_view.html",{"leaves":leaves})

def student_approve_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))

def student_disapprove_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def professeur_approve_leave(request,leave_id):
    leave=LeaveReportProfesseur.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("professeur_leave_view"))

def professeur_disapprove_leave(request,leave_id):
    leave=LeaveReportProfesseur.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("professeur_leave_view"))

def admin_view_attendance(request):
    matieres=Matieres.objects.all()
    session_year_id=SessionYearModel.objects.all()
    return render(request,"hod_template/admin_view_attendance.html",{"matieres":matieres,"session_year_id":session_year_id})

@csrf_exempt
def admin_get_attendance_dates(request):
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
def admin_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request,"hod_template/admin_profile.html",{"user":user})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))

def admin_send_notification_student(request):
    students=Students.objects.all()
    return render(request,"hod_template/student_notification.html",{"students":students})

def admin_send_notification_professeur(request):
    professeurs=Professeurs.objects.all()
    return render(request,"hod_template/professeur_notification.html",{"professeurs":professeurs})

@csrf_exempt
def send_student_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    student=Students.objects.get(admin=id)
    token=student.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Student Management System",
            "body":message,
            "click_action": "https://studentmanagementsystem22.herokuapp.com/student_all_notification",
            "icon": "http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationStudent(student_id=student,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_professeur_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    professeur=Professeurs.objects.get(admin=id)
    token=professeur.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Student Management System",
            "body":message,
            "click_action":"https://studentmanagementsystem22.herokuapp.com/professeur_all_notification",
            "icon":"http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationProfesseurs(professeur_id=professeur,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

def list_de_note_classe(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    
    annee_scolaire_id = request.GET.get('annee_scolaire', None)
    if annee_scolaire_id:
        annee_scolaire = get_object_or_404(SessionYearModel, pk=annee_scolaire_id)
    else:
        annee_scolaire = SessionYearModel.objects.filter(is_complete=False).first()

    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire).order_by('admin__first_name')
    
    buffer = BytesIO()

    # Ajuster les marges pour réduire l'espace vide
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)

    col_widths = [30, 150, 200, 60, 60, 60]
    table_data = [['N°', 'NOM', 'PRENOM', 'Notes de\nClasse', 'Devoir', 'Compo']] + \
                 [[str(i), eleve.admin.first_name, eleve.admin.last_name] for i, eleve in enumerate(eleves, start=1)]
    table = Table(table_data, colWidths=col_widths, rowHeights=None)

    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    elements = []
    heading_style = getSampleStyleSheet()['Heading2']
    heading_style.alignment = 1
    elements.append(Paragraph("LYCÉE DE SOTOUBOUA", heading_style))
    elements.append(Paragraph("Matière: "))
    elements.append(Paragraph("Coefficient: "))
    elements.append(Paragraph("Professeur: "))
    elements.append(Paragraph("Fiche de notes de la Classe de " + classe.classe_name, getSampleStyleSheet()['Heading1']))
    elements.append(table)
    footing_style = getSampleStyleSheet()['Heading3']
    footing_style.alignment = 2
    elements.append(Paragraph("Fait à Sotouboua le : ", footing_style))
    elements.append(Paragraph("   ", footing_style))
    elements.append(Paragraph("   ", footing_style))
    elements.append(Paragraph("Signature", footing_style))

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Fiche de notes de la classe de {classe.classe_name}.pdf"'
    response.write(pdf)
    return response


def list_eleve_classe_generate_pdf(request, classe_id):
    # Récupérer vos données depuis votre modèle ou toute autre source
   
    classe = get_object_or_404(Classes, pk=classe_id)
    
    annee_scolaire_id = request.GET.get('annee_scolaire', None)
    if annee_scolaire_id:
        annee_scolaire = get_object_or_404(SessionYearModel, pk=annee_scolaire_id)
    else:
        annee_scolaire = SessionYearModel.objects.filter(is_complete=False).first()

    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire).order_by('admin__first_name')
    

    # Créer un objet BytesIO pour stocker le PDF
    buffer = BytesIO()

    # Créer un SimpleDocTemplate pour gérer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Créer un tableau pour les données des élèves
    col_widths = [30, 150, 200, 80, 50, 50]
    table_data = [['N°', 'NOM', 'PRENOM', 'N° MATRICULE', 'SEXE', 'STATUT']] + \
                 [[str(i), eleve.admin.first_name, eleve.admin.last_name, eleve.numero_matricule, eleve.gender, eleve.statut] for i, eleve in enumerate(eleves, start=1)]
    table = Table(table_data, colWidths=col_widths, rowHeights=None)

    # Appliquer un style au tableau
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    # Ajouter le tableau au document
    elements = []
    # header_text = [
    #     "MINISTERE DES ENSEIGNEMENTS PRIMAIRE,",
    #     "SECONDAIRE, TECHNIQUE ET L'ARTISANAT",
    #     # ... autres lignes du header ...
    # ]

    # for line in header_text:
    #     elements.append(Paragraph(line, getSampleStyleSheet()['BodyText']))

    #  # Ajouter l'image
    # image_path = finders.find('assets/default/img/logo.jpg')
    # img = Image(image_path, width=100, height=110)
    # elements.append(img)
    heading_style = getSampleStyleSheet()['Heading2']
    heading_style.alignment = 1  # 0=Left, 1=Center, 2=Right
    elements.append(Paragraph("LYCÉE DE SOTOUBOUA", heading_style))
    elements.append(Paragraph("Liste de la Classe de " + classe.classe_name, getSampleStyleSheet()['Heading1']))
    elements.append(table)
    elements.append(Paragraph("TITULAIRE: "+ classe.titulaire.admin.first_name, heading_style))
    

    # Générer le PDF
    doc.build(elements)

    # Récupérer le contenu du buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Retourner le PDF en tant que réponse HTTP pour le téléchargement ou l'affichage
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Liste des eleves de la classe de {classe.classe_name}.pdf"'
    response.write(pdf)
    return response


def generate_professeur_list_pdf(request):
    # Récupérer vos données depuis votre modèle ou toute autre source
    profs = Professeurs.objects.all().order_by("admin__first_name")  # Remplacez YourModel par le nom de votre modèle
    
    
    # Créer un objet BytesIO pour stocker le PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Créer un tableau pour les données des élèves
    col_widths = [30, 200, 200, 100]
    table_data = [['N°', 'NOM', 'PRENOM', 'Nombres d\'élèves']] + \
                 [[str(i), prof.nom, prof.prenom, prof.nombre_eleves_enseignes()] for i, prof in enumerate(profs, start=1)]
    table = Table(table_data, colWidths=col_widths, rowHeights=None)

    # Appliquer un style au tableau
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    # Ajouter le tableau au document
    elements = []
    heading_style = getSampleStyleSheet()['Heading2']
    heading_style.alignment = 1  # 0=Left, 1=Center, 2=Right
    elements.append(Paragraph("LYCÉE DE SOTOUBOUA", heading_style))
    elements.append(table)
    

    # Générer le PDF
    doc.build(elements)

    # Récupérer le contenu du buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Retourner le PDF en tant que réponse HTTP pour le téléchargement ou l'affichage
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="example.pdf"'
    response.write(pdf)
    return response




def calculer_moyenne(evaluation_classe, devoir, composition):
    return (((evaluation_classe + devoir) / 2) + composition) / 2



def add_note_classe(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    matieres = Matieres.objects.filter(classe_id=classe)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire).order_by("admin__first_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)
    return render(request,"hod_template/Add_note_classe.html",
                  {
                    "matieres":matieres,
                    "classe":classe,
                    "eleves":eleves,
                    "trimestres":trimestres,
                 })

def add_note_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        
        matiere_name=request.POST.get("matiere_name")
        classe_id=request.POST.get("classe")
        coefficient=request.POST.get("coefficient")
        categorie_id=request.POST.get("categorie")
        categorie=CategorieMatiere.objects.get(id=categorie_id)
        classe=Classes.objects.get(id=classe_id)
        professeur_id=request.POST.get("professeur")
        professeur=Professeurs.objects.get(id=professeur_id)

        try:
            matiere=Matieres(matiere_name=matiere_name,classe_id=classe,professeur_id=professeur,categorie=categorie,coefficient=coefficient)
            matiere.save()
            messages.success(request,"Successfully Added Matiere")
            return HttpResponseRedirect(reverse("add_note_classe"))
        except Exception as e:
            messages.error(request,f"Failed to Add Matiere: {str(e)}")
            return HttpResponseRedirect(reverse("add_note_classe"))

def remplir_rang_matiere():
    # Récupérer toutes les notes
    notes = Note.objects.all()

    for note in notes:
        # Vérifier si le champ rang_matiere est vide
        if note.rang_matiere is None:
            # Calculer et attribuer le rang
            note.attribuer_rang_matiere()
            note.save()

    
def add_note(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    matieres = Matieres.objects.filter(classe_id=classe)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire).order_by("admin__first_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)

    if request.method == "POST":
        trimestre_id = request.POST.get("trimestre")
        matiere_id = request.POST.get("matiere")
        matiere = Matieres.objects.get(pk=matiere_id)
        
        # Récupérer l'instance du trimestre
        trimestre = Periode.objects.get(id=trimestre_id)
        numero_matiere = request.POST.get('numero_matiere')
        if numero_matiere:
            numero_matiere=numero_matiere
        elif numero_matiere=='':
            numero_matiere=1
        
        existing_note = Note.objects.filter(
            matiere=matiere,
            trimestre=trimestre  # Utiliser l'instance du trimestre ici
        ).first()

        if existing_note:
            messages.error(request, f"Une note existe déjà pour {matiere.matiere_name} pour ce trimestre.")
        else:
            for eleve in eleves:
                evaluation_classe = request.POST.get(f"evaluation_classe_{eleve.id}")
                devoir = request.POST.get(f"devoir_{eleve.id}")
                composition = request.POST.get(f"composition_{eleve.id}")
                
                coefficient_matiere = matiere.coefficient
            
                note = Note.objects.create(
                    eleve=eleve,
                    matiere=matiere,
                    coefficient=coefficient_matiere,
                    numero_matiere=numero_matiere,
                    evaluation_classe=evaluation_classe,
                    devoir=devoir,
                    composition=composition,
                    trimestre=trimestre  # Utiliser l'instance du trimestre ici
                )
                note.save()
                messages.success(request, "Les notes ont été ajoutées et les calculs effectués avec succès!")
                
                # Calculer la moyenne de la matière
                note.calculer_moyenne_matiere()

                # Attribuer le rang dans la matière
                note.attribuer_rang_matiere()
            
        for matiere in matieres:
            matiere.possede_deja_notes = Note.objects.filter(matiere=matiere, trimestre=trimestre).exists()

        # Effectuer les calculs de moyenne trimestrielle et annuelle
        for eleve in eleves:
            # Calculer la moyenne trimestrielle pour l'élève
            eleve.calculer_moyenne_par_periode(trimestre)

            # Attribuer le rang trimestriel
            eleve.attribuer_rang_par_periode(trimestre)

            # Calculer la moyenne annuelle pour l'élève
            eleve.calculer_moyenne_annuelle(annee_scolaire)

            # Attribuer le rang annuel
            eleve.attribuer_rang_annuel(annee_scolaire)
            
    return render(request, 'hod_template/Add_note.html', {'classe': classe, 'eleves': eleves, 'matieres': matieres, 'trimestres': trimestres})
   
def add_note_Examen(request, examen_blanc_id):
    examen_blanc = get_object_or_404(ExamenBlanc, pk=examen_blanc_id)
    classe_concerne = examen_blanc.classes_concernees.all().first()
    matieres = Matieres.objects.filter(classe_id=classe_concerne)
    eleves = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc).order_by("numero_table")
    
    
    if request.method == "POST":
        matiere_id = request.POST.get("matiere")
        matiere = Matieres.objects.get(pk=matiere_id)
        
        examen_id = request.POST.get("examen")
       
        examen = ExamenBlanc.objects.get(nom=examen_id)
        
        
        existing_note = ExamenNote.objects.filter(
            matiere=matiere,
            examen=examen_blanc  # Utiliser l'instance du trimestre ici
        ).first()

        if existing_note:
            messages.error(request, f"Une note existe déjà pour {matiere.matiere_name} pour cet Examen.")
        else:
            for eleve in eleves:
                numero_matiere = request.POST.get('numero_matiere')
                note = request.POST.get(f"note_{eleve}")
                
                coefficient_matiere = matiere.coefficient
                print(f"examen : {examen}")
                print(f"matiere : {matiere}")
                print(f"coefficient : {coefficient_matiere}")
                print(f"numero_table_eleve : {eleve}")
                print(f"numero_matiere : {numero_matiere}")
                print(f"note : {note}")
            
                note = ExamenNote.objects.create(
                    examen=examen,
                    matiere=matiere,
                    coefficient=coefficient_matiere,
                    numero_table_eleve=eleve,
                    numero_matiere=numero_matiere,
                    note=note,
                )
                note.save()
                # Attribuer le rang dans la matière
                note.attribuer_rang_matiere()
            
            messages.success(request, "Les notes ont été ajoutées et les calculs effectués avec succès!")
                

                
        for matiere in matieres:
            matiere.possede_deja_notes = ExamenNote.objects.filter(matiere=matiere, examen=examen_blanc).exists()

        

        
    return render(request, 'hod_template/Add_note_Examen.html', { 
                                                          'matieres': matieres,
                                                          'examen_blanc':examen_blanc,
                                                           'eleves':eleves,
                                                          })

def add_note1(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    matieres = Matieres.objects.filter(classe_id=classe)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire).order_by("admin__first_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)

    if request.method == "POST":
        trimestre_id = request.POST.get("trimestre")
        matiere_id = request.POST.get("matiere")
        matiere = Matieres.objects.get(pk=matiere_id)
        numero_matiere = request.POST.get('numero_matiere')
        # Récupérer l'instance du trimestre
        trimestre = Periode.objects.get(id=trimestre_id)
        
        existing_note = Note.objects.filter(
            matiere=matiere,
            trimestre=trimestre
        ).first()

        if existing_note:
            messages.error(request, f"Une note existe déjà pour {matiere.matiere_name} pour ce trimestre.")
        else:
            for eleve in eleves:
                
                
                # Validation et gestion des valeurs vides
                evaluation_classe = request.POST.get(f"evaluation_classe_{eleve.id}")
                devoir = request.POST.get(f"devoir_{eleve.id}")
                composition = request.POST.get(f"composition_{eleve.id}")
                
                # Convertir les champs en décimal et gérer les valeurs vides
                try:
                    numero_matiere = int(numero_matiere) if numero_matiere else 1
                    evaluation_classe = float(evaluation_classe) if evaluation_classe else 0.0
                    devoir = float(devoir) if devoir else 0.0
                    composition = float(composition) if composition else 0.0
                except ValueError:
                    messages.error(request, f"Les valeurs pour {eleve.admin.first_name} {eleve.admin.last_name} doivent être des nombres décimaux.")
                    continue
                
                coefficient_matiere = matiere.coefficient
            
                note = Note.objects.create(
                    eleve=eleve,
                    matiere=matiere,
                    coefficient=coefficient_matiere,
                    numero_matiere=numero_matiere,
                    evaluation_classe=evaluation_classe,
                    devoir=devoir,
                    composition=composition,
                    trimestre=trimestre
                )
                note.save()
                messages.success(request, "Les notes ont été ajoutées et les calculs effectués avec succès!")
                
                # Calculer la moyenne de la matière
                note.calculer_moyenne_matiere()

                # Attribuer le rang dans la matière
                note.attribuer_rang_matiere()

        for matiere in matieres:
            matiere.possede_deja_notes = Note.objects.filter(matiere=matiere, trimestre=trimestre).exists()

        # Effectuer les calculs de moyenne trimestrielle et annuelle
        for eleve in eleves:
            # Calculer la moyenne trimestrielle pour l'élève
            eleve.calculer_moyenne_par_periode(trimestre)

            # Attribuer le rang trimestriel
            eleve.attribuer_rang_par_periode(trimestre)

            # Calculer la moyenne annuelle pour l'élève
            eleve.calculer_moyenne_annuelle(annee_scolaire)

            # Attribuer le rang annuel
            eleve.attribuer_rang_annuel(annee_scolaire)

    return render(request, 'hod_template/Add_note.html', {'classe': classe, 'eleves': eleves, 'matieres': matieres, 'trimestres': trimestres})

def attribuer_rang_matiere(matiere, trimestre):
    # Récupérer les notes pour la matière et le trimestre donnés
    notes = Note.objects.filter(matiere=matiere, trimestre=trimestre).order_by('-moyenne_matiere')
    
    rang = 1
    for note in notes:
        note.rang_matiere = rang
        note.save()
        rang += 1
        
def attribuer_rang_matiere_examen(examen, matiere):
    # Récupérer les notes pour la matière et le trimestre donnés
    notes = ExamenNote.objects.filter(matiere=matiere, examen=examen).order_by('-note')
    
    rang = 1
    for note in notes:
        note.rang_matiere = rang
        note.save()
        rang += 1

def view_note_Examen(request, examen_blanc_id):
    examen_blanc = get_object_or_404(ExamenBlanc, pk=examen_blanc_id)
    classe_concerne = examen_blanc.classes_concernees.all().first()
    matieres = Matieres.objects.filter(classe_id=classe_concerne)
    eleves = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc).order_by("numero_table")
    

    matiere_id = request.GET.get('matiere', None)
    if matiere_id:
        matiere_selected = get_object_or_404(Matieres, pk=matiere_id)
    else:
        matiere_selected = matieres.first()

    for matiere in matieres:
        matiere.possede_deja_notes = ExamenNote.objects.filter(matiere=matiere, examen=examen_blanc).exists()

    # Calculer les rangs avant l'annotation des élèves
    #attribuer_rang_matiere(matiere_selected, trimestre_selected)
    attribuer_rang_matiere_examen(examen_blanc, matiere_selected)

    # Subquery pour obtenir les notes
    notes_subquery = ExamenNote.objects.filter(
        matiere=matiere_selected,
        examen=examen_blanc,
        numero_table_eleve=OuterRef('pk')
    ).values('id', 'note', 'rang_matiere')[:1]

    # Annotation des élèves avec leurs notes
    eleves = eleves.annotate(
        note_id=Subquery(notes_subquery.values('id')),
        note=Coalesce(Subquery(notes_subquery.values('note')), Cast(0, output_field=DecimalField())),
        
        rang_matiere=Coalesce(Subquery(notes_subquery.values('rang_matiere')), Cast(0, output_field=IntegerField()))
    )
    notes = ExamenNote.objects.filter(examen=examen_blanc, matiere=matiere_selected)

    return render(request, 'hod_template/view_note_Examen.html', {
        'examen_blanc': examen_blanc,
        'eleves': eleves,
        'matieres': matieres,
        'matiere_selected': matiere_selected,
        'notes': notes,
    })

def view_note(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    matieres = Matieres.objects.filter(classe_id=classe.id).order_by("matiere_name")
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire).order_by("admin__first_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)

    matiere_id = request.GET.get('matiere', None)
    if matiere_id:
        matiere_selected = get_object_or_404(Matieres, pk=matiere_id)
    else:
        matiere_selected = matieres.first()

    trimestre_id = request.GET.get('trimestre', None)
    if trimestre_id:
        trimestre_selected = get_object_or_404(Periode, pk=trimestre_id)
    else:
        trimestre_selected = Periode.objects.filter(annee_scolaire=annee_scolaire).first()

    for matiere in matieres:
        matiere.possede_deja_notes = Note.objects.filter(matiere=matiere, trimestre=trimestre_selected).exists()

    # Calculer les rangs avant l'annotation des élèves
    attribuer_rang_matiere(matiere_selected, trimestre_selected)

    # Subquery pour obtenir les notes
    notes_subquery = Note.objects.filter(
        matiere=matiere_selected,
        trimestre=trimestre_selected,
        eleve_id=OuterRef('pk')
    ).values('id', 'evaluation_classe', 'devoir', 'composition', 'moyenne_matiere', 'rang_matiere')[:1]

    # Annotation des élèves avec leurs notes
    eleves = eleves.annotate(
        note_id=Subquery(notes_subquery.values('id')),
        evaluation_classe=Coalesce(Subquery(notes_subquery.values('evaluation_classe')), Cast(0, output_field=DecimalField())),
        devoir=Coalesce(Subquery(notes_subquery.values('devoir')), Cast(0, output_field=DecimalField())),
        composition=Coalesce(Subquery(notes_subquery.values('composition')), Cast(0, output_field=DecimalField())),
        moyenne_matiere=Coalesce(Subquery(notes_subquery.values('moyenne_matiere')), Cast(0, output_field=DecimalField())),
        rang_matiere=Coalesce(Subquery(notes_subquery.values('rang_matiere')), Cast(0, output_field=IntegerField()))
    )
    notes = Note.objects.filter(trimestre=trimestre_selected, matiere=matiere_selected)

    return render(request, 'hod_template/view_note.html', {
        'classe': classe,
        'eleves': eleves,
        'matieres': matieres,
        'matiere_selected': matiere_selected,
        'trimestres': trimestres,
        'trimestre_selected': trimestre_selected,
        'notes': notes,
    })

def edit_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    classe_id = note.eleve.classe_id.id  # Obtenir le classe_id depuis l'élève lié à la note

    if request.method == 'POST':
        note.evaluation_classe = request.POST.get('evaluation_classe')
        note.devoir = request.POST.get('devoir')
        note.composition = request.POST.get('composition')
        note.calculer_moyenne_matiere()  # Assurez-vous que cette méthode existe
        note.save()
        
        # Calculer la moyenne de la matière
        note.calculer_moyenne_matiere()

        # Attribuer le rang dans la matière
        note.attribuer_rang_matiere()
        

        messages.success(request, "La note a été mise à jour avec succès.")
        return redirect('view_note', classe_id=classe_id)  # Redirection avec classe_id
    
    return redirect('view_note', classe_id=classe_id)  # Redirection avec classe_id

def create_note(request, eleve_id):
    eleve = get_object_or_404(Students, pk=eleve_id)
    matiere_id = request.GET.get('matiere')
    trimestre_id = request.GET.get('trimestre')
    classe_id = eleve.classe_id.id  # Extraire l'identifiant de la classe

    # Vérifier si 'matiere_id' et 'trimestre_id' sont présents dans la requête
    if not matiere_id or not trimestre_id:
        messages.error(request, "Matière ou trimestre manquant.")
        return redirect('view_note', classe_id=classe_id)

    # Utiliser get_object_or_404 pour la matière
    matiere = get_object_or_404(Matieres, id=matiere_id)
    coefficient_matiere = matiere.coefficient

    if request.method == 'POST':
        evaluation_classe = request.POST.get('evaluation_classe')
        devoir = request.POST.get('devoir')
        composition = request.POST.get('composition')

        note = Note.objects.create(
            eleve=eleve,
            matiere=matiere,
            trimestre_id=trimestre_id,
            coefficient=coefficient_matiere,
            evaluation_classe=evaluation_classe,
            devoir=devoir,
            composition=composition
        )
        # Calculer la moyenne de la matière
        note.calculer_moyenne_matiere()

        # Attribuer le rang dans la matière
        note.attribuer_rang_matiere()
        remplir_rang_matiere()


        messages.success(request, "La note a été ajoutée avec succès.")
        return redirect('view_note', classe_id=classe_id)

    return redirect('view_note', classe_id=classe_id)

def calculer_moyenne_par_periode(eleve, periode):
    notes = Note.objects.filter(eleve=eleve, trimestre=periode)
    if notes.exists():
        total = 0
        total_coefficients = 0
        
        for note in notes:
            moyenne_matiere = note.moyenne_matiere or 0
            coefficient = note.coefficient or 1  # Utilisez 1 comme coefficient par défaut s'il est None
            
            total += moyenne_matiere * coefficient
            total_coefficients += coefficient
        # Calculer la moyenne en toute sécurité
        moyenne = total / total_coefficients if total_coefficients > 0 else 0
        
        # Créer ou mettre à jour la moyenne pour cette période
        moyenne_obj, created = Moyenne.objects.update_or_create(
            eleve=eleve, 
            periode=periode, 
            defaults={'moyenne': moyenne}
        )
        return moyenne_obj
    return None

def attribuer_rang_par_periode_et_classe(periode, classe):
    moyennes = Moyenne.objects.filter(periode=periode, eleve__classe_id=classe).order_by('-moyenne')
    for index, moyenne in enumerate(moyennes):
        moyenne.rang = index + 1
        moyenne.save()
        
def attribuer_rang_examen(examen_blanc):
    moyennes = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc).order_by('-moyenne')
    for index, moyenne in enumerate(moyennes):
        moyenne.rang = index + 1
        moyenne.save()

def calculer_moyenne_examen(numero_table_eleve, examen_blanc):
    notes = ExamenNote.objects.filter(examen=examen_blanc, numero_table_eleve=numero_table_eleve)
    if notes.exists():
        total = 0
        total_coefficients = 0
        
        for note in notes:
            moyenne_matiere = note.note or 0
            coefficient = note.coefficient or 1  # Utilisez 1 comme coefficient par défaut s'il est None
            
            total += moyenne_matiere * coefficient
            total_coefficients += coefficient
        # Calculer la moyenne en toute sécurité
        moyenne = total / total_coefficients if total_coefficients > 0 else 0
        
        # Créer ou mettre à jour la moyenne pour cette période
        moyenne_obj, created = NumeroTableExamen.objects.update_or_create(
            examen_blanc=examen_blanc, 
            numero_table=numero_table_eleve.numero_table, 
            defaults={'moyenne': moyenne}
        )
        return moyenne_obj
    return None

def view_exam_results(request, examen_blanc_id):
    examen_blanc = get_object_or_404(ExamenBlanc, pk=examen_blanc_id)
    classe_concerne = examen_blanc.classes_concernees.all().first()
    matieres = Matieres.objects.filter(classe_id=classe_concerne)
    eleves = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc).order_by("rang")
    
    for matiere in matieres:
        matiere.possede_deja_notes = ExamenNote.objects.filter(matiere=matiere, examen=examen_blanc).exists()

    for numero_table_eleve in eleves:
        calculer_moyenne_examen(numero_table_eleve, examen_blanc)
        
    attribuer_rang_examen(examen_blanc)
    
    moyennes_classe = MoyenneExamen.objects.filter(examen=examen_blanc)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
        
    # Annotation des élèves avec les moyennes des matières
    for eleve in eleves:
        eleve.moyennes_matieres = [
            eleve.examen_notes.filter(matiere=matiere, examen=examen_blanc).first()
            for matiere in matieres
        ]
        
    #eleves = sorted(eleves, key=lambda e: e.rang if e.rang is not None else float('inf'))
    #eleves = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc).order_by("rang")
                    
    return render(request, 'hod_template/view_exam_results.html', {
        'examen_blanc': examen_blanc,
        'eleves': eleves,
        'matieres': matieres,
        'moyenne_max':moyenne_max,
        'moyenne_min':moyenne_min,
        'moyenne_generale':moyenne_generale
    })

def view_classe_results(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire)
    matieres = Matieres.objects.filter(classe_id=classe.id).order_by("matiere_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)
    trimestre_selected = Periode.objects.filter(annee_scolaire=annee_scolaire).first()
    
    trimestre_id = request.GET.get('trimestre', None)
    if trimestre_id:
        trimestre_selected = get_object_or_404(Periode, pk=trimestre_id)
    else:
        trimestre_selected = Periode.objects.filter(annee_scolaire=annee_scolaire).first()
    

    for matiere in matieres:
        matiere.possede_deja_notes = Note.objects.filter(matiere=matiere, trimestre=trimestre_selected).exists()


    # Boucle pour s'assurer que les moyennes manquantes sont calculées
    for eleve in eleves:
        for matiere in matieres:
            notes = Note.objects.filter(eleve=eleve, matiere=matiere, trimestre=trimestre_selected)
            
            if notes.exists():
                total_moyenne = 0
                count = 0
                
                for note in notes:
                    # Calculer la moyenne de chaque note
                    moyenne_note = calculer_moyenne(
                        note.evaluation_classe,
                        note.devoir,
                        note.composition
                    )
                    total_moyenne += moyenne_note
                    count += 1
                
                # Calculer la moyenne globale
                moyenne_matiere = total_moyenne / count if count > 0 else 0

                # Nettoyer les doublons existants pour cette combinaison
                RangMatiere.objects.filter(
                    eleve=eleve,
                    matiere=matiere,
                    periode=trimestre_selected
                ).delete()

                # Créer une nouvelle entrée pour la combinaison
                RangMatiere.objects.create(
                    eleve=eleve,
                    matiere=matiere,
                    periode=trimestre_selected,
                    moyenne_matiere=moyenne_matiere
                )

     # Calculer les moyennes trimestrielles pour chaque élève
    for eleve in eleves:
        
        calculer_moyenne_par_periode(eleve, trimestre_selected)
    
    # Attribuer les rangs en fonction de la classe pour chaque période
    attribuer_rang_par_periode_et_classe(trimestre_selected, classe)

    # Récupérer les moyennes et les rangs pour chaque élève pour le template
    for eleve in eleves:
        moyenne_trimestre_obj = Moyenne.objects.filter(
            eleve=eleve,
            periode=trimestre_selected
        ).first()
        if moyenne_trimestre_obj:
            eleve.moyenne_trimestre = moyenne_trimestre_obj.moyenne
            eleve.rang_trimestre = moyenne_trimestre_obj.rang
        else:
            eleve.moyenne_trimestre = None
            eleve.rang_trimestre = None
           
    # Annotation des élèves avec les moyennes des matières
    for eleve in eleves:
        eleve.moyennes_matieres = [
            eleve.rangs_matiere.filter(matiere=matiere, periode=trimestre_selected).first()
            for matiere in matieres
        ]
    
    moyennes_classe = Moyenne.objects.filter(eleve__classe_id=classe, periode=trimestre_selected)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    
    eleve = eleves.first()
     # Calculer la moyenne annuelle si toutes les périodes ont des valeurs
    
    for periode in trimestres:
        try: 
            Moyenne.objects.get(eleve=eleve, periode=periode)
            toutes_periodes_avant=True
        except:
            toutes_periodes_avant = False
    
    eleves = sorted(eleves, key=lambda e: e.rang_trimestre if e.rang_trimestre is not None else float('inf'))
      
    return render(request, 'hod_template/view_classe_results.html', {
        'classe': classe,
        'eleves': eleves,
        'toutes_periodes_avant': toutes_periodes_avant,
        'matieres': matieres,
        'trimestres': trimestres,
        'trimestre_selected': trimestre_selected,
        'moyenne_max':moyenne_max,
        'moyenne_min':moyenne_min,
        'moyenne_generale':moyenne_generale
    })


def view_studen_results(request, trimestre_id, eleve_id):
    eleve = get_object_or_404(Students, pk=eleve_id)
    trimestre = get_object_or_404(Periode, pk=trimestre_id)
    classe = eleve.classe_id
    annee_scolaire = SessionYearModel.get_current_session()
    notes = Note.objects.filter(eleve=eleve, trimestre=trimestre).order_by('numero_matiere') 

    # Calculate required values
    for note in notes:
        # Calculez la moyenne_note pour chaque note
        note.moyenne_note = (((note.evaluation_classe + note.devoir)/2) + note.composition) / 2
        note.moyenne_ponderee = note.moyenne_note * note.coefficient
        
         # Mettre à jour le rang_matiere à partir de la table RangMatiere
        rang_matiere_obj = RangMatiere.objects.filter(
            eleve=eleve,
            matiere=note.matiere,
            periode=trimestre
        ).first()

        if rang_matiere_obj:
            note.rang_matiere = rang_matiere_obj.rang
            note.save()

    total_coefficients = sum(note.coefficient for note in notes)
    total_pondered = sum(note.moyenne_ponderee for note in notes)
    
    moyennes_par_categorie = {}
    for note in notes:
        categorie = note.matiere.categorie.nom
        if categorie not in moyennes_par_categorie:
            moyennes_par_categorie[categorie] = note.calculer_moyenne_categorie()
    
    moyennes_classe = Moyenne.objects.filter(eleve__classe_id=classe, periode=trimestre)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    
    moyenne_trimestre_obj = Moyenne.objects.get(eleve=eleve, periode=trimestre)
    moyenne_trimestre = moyenne_trimestre_obj.moyenne if moyenne_trimestre_obj else None
    rang_trimestre = moyenne_trimestre_obj.rang if moyenne_trimestre_obj else None

    remplir_rang_matiere()
    
    # Check if the 'Imprimer Le bulletin' button was pressed
    if 'imprimer' in request.GET:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Bulletin_{eleve.admin.last_name}_{eleve.admin.first_name}.pdf"'

        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Add title and student info
        elements.append(Paragraph(f"Bulletin de {eleve.admin.first_name} {eleve.admin.last_name}", styles['Title']))
        elements.append(Paragraph(f"Classe : {classe.classe_name} | Trimestre : {trimestre.periode_name}", styles['Normal']))
        elements.append(Paragraph(f"Moyenne : {moyenne_trimestre} | Rang : {rang_trimestre}", styles['Normal']))
        elements.append(Paragraph(f"Moyenne la plus élevée : {moyenne_max} | Moyenne la plus faible : {moyenne_min}", styles['Normal']))
        elements.append(Paragraph(f"Moyenne générale de la classe : {moyenne_generale}", styles['Normal']))

        # Add table of notes
        data = [
            ['Matière', 'Évaluation classe', 'Devoir', 'Composition', 'Moyenne Note', 'Coefficient', 'Moyenne Pondérée', 'Rang', 'Observation', 'Prof chargé']
        ]
        for note in notes:
            data.append([
                note.matiere.matiere_name,
                note.evaluation_classe,
                note.devoir,
                note.composition,
                round(note.moyenne_note, 2),
                note.coefficient,
                round(note.moyenne_ponderee, 2),
                note.rang_matiere,
                'FAIBLE' if note.moyenne_note <= 5 else 'INSUFFISANT' if 5 < note.moyenne_note < 9 else 'PASSABLE' if 9 <= note.moyenne_note < 12 else 'ASSEZ BIEN' if 12 <= note.moyenne_note < 14 else 'BIEN' if 14 <= note.moyenne_note < 16 else 'TRÈS BIEN' if 16 <= note.moyenne_note < 18 else 'EXCELLENT',
                note.matiere.professeur_id.admin.first_name,
            ])

        # Add totals row
        data.append([
            'Totaux :', '', '', '', '', total_coefficients, round(total_pondered, 2), '', '', ''
        ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Build PDF
        doc.build(elements)
        return response

    return render(request, 'hod_template/view_studen_results.html', {
        'classe': classe,
        'notes': notes,
        'eleve': eleve,
        'trimestre': trimestre,
        'total_coefficients': total_coefficients,
        'total_pondered': total_pondered,
        'moyenne_trimestre': moyenne_trimestre,
        'rang_trimestre': rang_trimestre,
        'moyenne_generale': moyenne_generale,
        'moyenne_min': moyenne_min,
        'moyenne_max': moyenne_max,
        'moyennes_par_categorie': moyennes_par_categorie,
    })

#======================================= PDF ===============================================================
@staticmethod
def download_class_reports(request, trimestre_id, classe_id):
    # Récupérer la classe
    trimestre = get_object_or_404(Periode, pk=trimestre_id)
    classe = Classes.objects.get(pk=classe_id)
    eleves = classe.students.all()

    # Créer un objet BytesIO pour stocker l'archive ZIP
    zip_buffer = BytesIO()

    # Créer l'archive ZIP
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as report_zip:
        for eleve in eleves:
            # Générer le bulletin pour chaque élève
            eleve_report = generate_bulletin_pdf(request, trimestre.id, eleve.id)

            # Ajouter le bulletin à l'archive avec un nom de fichier spécifique (nom_prenom.pdf)
            report_zip.writestr(f"{eleve.admin.first_name}_{eleve.admin.last_name}.pdf", eleve_report.content)

    # Finaliser l'archive ZIP
    zip_buffer.seek(0)

    # Créer une réponse HTTP avec l'archive ZIP en tant que contenu
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{classe.classe_name}_reports.zip"'

    return response

#======================================
def generate_bulletin_pdf1(request, trimestre_id, eleve_id):
    eleve = get_object_or_404(Students, pk=eleve_id)
    trimestre = get_object_or_404(Periode, pk=trimestre_id)
    annee_scolaire = trimestre.annee_scolaire
    classe = eleve.classe_id
    
    classes_info = Classes.objects.annotate(nombre_eleves=Count('students')).select_related('titulaire__admin')
    # Trouver les informations de la classe de l'élève dans le résultat annoté
    classe_annotated_info = classes_info.filter(id=classe.id).first()

    if classe_annotated_info:
        effectif_classe = classe_annotated_info.nombre_eleves
    else:
        print("Classe non trouvée ou aucun effectif annoté pour cette classe")


    # Ajouter les notes
    notes = Note.objects.filter(eleve=eleve, trimestre=trimestre).order_by('numero_matiere')
    for note in notes:
        # Calculez la moyenne_note pour chaque note
        note.moyenne_note = (((note.evaluation_classe + note.devoir)/2) + note.composition) / 2
        note.moyenne_ponderee = note.moyenne_note * note.coefficient
        
         # Mettre à jour le rang_matiere à partir de la table RangMatiere
        rang_matiere_obj = RangMatiere.objects.filter(
            eleve=eleve,
            matiere=note.matiere,
            periode=trimestre
        ).first()

        if rang_matiere_obj:
            note.rang_matiere = rang_matiere_obj.rang
            note.save()

    # Vérifier si l'élève est inapte au sport
    if eleve.aptitude_sport == 'Inapte':
        total_coefficients = sum(note.coefficient for note in notes if note.matiere.matiere_name != 'EPS')
        total_pondered = sum(note.moyenne_ponderee for note in notes if note.matiere.matiere_name != 'EPS' and note.moyenne_ponderee is not None)
    else:
        total_coefficients = sum(note.coefficient for note in notes)
        total_pondered = sum(note.moyenne_ponderee if note.moyenne_ponderee is not None else Decimal(0) for note in notes)

    # Calculer la moyenne trimestrielle
    moyenne_trimestrielle = total_pondered / total_coefficients if total_coefficients > 0 else 0

    
    moyennes_par_categorie = {}
    for note in notes:
        categorie = note.matiere.categorie.nom
        if categorie not in moyennes_par_categorie:
            moyennes_par_categorie[categorie] = note.calculer_moyenne_categorie()
            
        # Dictionnaire pour stocker les notes par catégorie
    notes_par_categorie = {}

    # Grouper les notes par catégorie de matière
    for note in notes:
        categorie = note.matiere.categorie.nom
        if categorie not in notes_par_categorie:
            notes_par_categorie[categorie] = []
        notes_par_categorie[categorie].append(note)

    
    moyennes_classe = Moyenne.objects.filter(eleve__classe_id=classe, periode=trimestre)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    
    moyenne_trimestre_obj = Moyenne.objects.get(eleve=eleve, periode=trimestre)
    moyenne_trimestre = moyenne_trimestre_obj.moyenne if moyenne_trimestre_obj else None
    rang_trimestre = moyenne_trimestre_obj.rang if moyenne_trimestre_obj else None

    
    
    # Créer un objet BytesIO pour stocker le PDF
    buffer = BytesIO()
    
    # Créer un canvas PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    c = my_temp(c)

    c.setStrokeColorRGB(0.1,0.8,0.1)
    c.setFillColorRGB(0,0,0)

    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(35, 8.1*inch, f"BULLETIN DE NOTES DU {trimestre.periode_name}")
    
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0, 7.8*inch, "Nom : " + eleve.admin.first_name) 
    c.drawString(0, 7.5*inch, "Prénom : " + eleve.admin.last_name)
    c.drawString(0, 7.2*inch, "Sexe : " + eleve.gender)
    c.drawString(80, 7.2*inch, "Statut : " + eleve.statut)
    c.drawString(200, 7.2*inch, "N° Matricule : " + eleve.numero_matricule)
    c.drawString(0, 6.9*inch, "Date de Naissance: " + eleve.date_naissance.strftime('%d-%b-%Y'))
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(4.8*inch, 9.0*inch, 'Année Scolaire: ' + f" {annee_scolaire}")
    table_classe = [
        ["CLASSE", "EFFECTIF"],
        [classe.classe_name, str(effectif_classe)],
        
    ]

    # Dessiner le tableau
    table = Table(table_classe, colWidths=[100, 60], rowHeights=14)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 12)
    ]))

    table.wrapOn(c, 4.8*inch, 8.5*inch,)
    table.drawOn(c, 4.8*inch, 8.5*inch,)
    
    # Récupérer le chemin de l'image de profil de l'élève
    image_path = settings.BASE_DIR + eleve.profile_pic.name
    # Vérifier si le fichier existe
    if not os.path.exists(image_path):
        raise OSError(f"Cannot open resource: {image_path}")
    
    if image_path:
        # Dessiner l'image sur le PDF
        c.drawImage(image_path, 5.5 * inch, 6.8 * inch, width=100, height=120)
    else:
        print("Image non trouvée")
    

    col_widths = [90, 50, 50, 50, 50, 30, 50,40,100, 80]

    # Convertir le HTML en tableau pour l'ajouter au PDF
    for categorie, notes in notes_par_categorie.items():
        totals_row = [
        ['Totaux :', '', '', '', '', f'{total_coefficients}', f'{"{:.2f}".format(total_pondered)}']
        + [''] * 2  # Ajouter des colonnes vides pour compenser
        ]
        # Préparer les données pour le tableau des notes
        data = [['Catégorie', 'Matières', 'Notes de\n classe', 'Devoir', 'Compo', 'Moy', 'Coef', 'Notes', 'Rang', 'Observations', 'Prof chargé']]

        
        # Ajouter une ligne pour la catégorie
        data.append([categorie] + [''] * 10)
        
        for note in notes:
            data.append([
                '',  # Catégorie vide pour les lignes suivantes
                note.matiere.matiere_name, 
                'Inapte' if note.matiere.matiere_name == 'EPS' and eleve.aptitude_sport == 'Inapte' else note.evaluation_classe, 
                'Inapte' if note.matiere.matiere_name == 'EPS' and eleve.aptitude_sport == 'Inapte' else note.devoir, 
                'Inapte' if note.matiere.matiere_name == 'EPS' and eleve.aptitude_sport == 'Inapte' else note.composition, 
                '  ' if note.matiere.matiere_name == 'EPS' and eleve.aptitude_sport == 'Inapte' else "{:.2f}".format(note.moyenne_note),
                note.coefficient, 
                "{:.2f}".format(note.moyenne_ponderee) if note.moyenne_ponderee is not None else ' ',  
                '  ' if note.matiere.matiere_name == 'EPS' and eleve.aptitude_sport == 'Inapte' else f"{note.rang_matiere}{'er' if note.rang_matiere == 1 and eleve.gender == 'M' else 'ère' if note.rang_matiere == 1 and eleve.gender == 'F' else 'ème'}", 
                'INAPTE' if note.matiere.matiere_name == 'EPS' and eleve.aptitude_sport == 'Inapte' else 'TRÈS FAIBLE' if note.moyenne_note < 5 else 
                'FAIBLE' if 5 <= note.moyenne_note < 7 else 
                'TRÈS INSUFFISANT' if 7 <= note.moyenne_note < 8 else 
                'INSUFFISANT' if 8 <= note.moyenne_note < 10 else 
                'PASSABLE' if 10 <= note.moyenne_note < 12 else 
                'ASSEZ BIEN' if 12 <= note.moyenne_note < 14 else 
                'BIEN' if 14 <= note.moyenne_note < 16 else 
                'TRÈS BIEN' if 16 <= note.moyenne_note < 18 else 
                'EXCELLENT' , 
                note.matiere.professeur_id.admin.first_name
            ])

    data.extend(totals_row)

    # Créer le tableau
    table = Table(data, colWidths=col_widths, rowHeights=None)
    # Appliquer un style au tableau
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    # Positionner le tableau sur le canevas
    table.wrapOn(c, 0, 0)
    table.drawOn(c, -60, 270)
    
    table_classe = [
        ["Catégorie Matière", "Moyenne"],
        
        
    ] 
    for categorie, moyenne in moyennes_par_categorie.items():
        table_classe.append([
            categorie,
            "{:.2f}".format(moyenne),
        ])

    # Dessiner le tableau
    table = Table(table_classe, colWidths=[200, 60], rowHeights=14)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 12)
    ]))
    
    table.wrapOn(c, -0.4 * inch, 3.3 * inch)
    table.drawOn(c, -0.4 * inch, 2.5 * inch)

    
    c.setFont("Helvetica-Bold", 14)

    c.drawString(1.8 * inch, 1 * inch, "Observations du conseil")
    c.drawString(1.8 * inch, 0.8 * inch, "______________________")
    c.drawString(1.8 * inch, 0.5 * inch, "______________________")

    c.setFont("Helvetica-Bold", 12)
    import locale
    from datetime import date

    #locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

    # Obtenir la date d'aujourd'hui
    dt = date.today().strftime("%d-%b-%Y")

    c.drawString(4.8 * inch, 1 * inch, "Sotouboua, le " + dt)

    c.setFont("Helvetica-Oblique", 12)
    c.drawString(5.3 * inch, 0.6 * inch, "Le Proviseur")
    

    # Tableau de disciplines et d'observations
    # table_disciplines = [
    #     ["FELICITATIONS", ""],
    #     ["ENCOURAGEMENTS", ""],
    #     ["TABLEAU D'HONNEUR", ""]
    # ]

    # # Dessiner le tableau
    # table = Table(table_disciplines, colWidths=[114, 40], rowHeights=14)
    # table.setStyle(TableStyle([
    #     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    #     ('GRID', (0, 0), (-1, -1), 1, colors.black),
    #     ('FONTSIZE', (0, 0), (-1, -1), 8)
    # ]))

    # table.wrapOn(c, -0.4 * inch, 2.3 * inch)
    # table.drawOn(c, -0.4 * inch, 2.3 * inch)

    # Les sections AVERTISSEMENT et BLAME (sans données)
    # Créer des tables vides pour ces sections

    empty_table_avertissement = [
        ["Absences", ""],
        ["Retards", ""],
        ["Travail", ""],
        ["Discipline", ""],
        ["Exclusions", ""],
    ]

    empty_table_blame = [
        ["Travail", ""],
        ["Discipline", ""],
    ]

    # Tableau pour AVERTISSEMENT
    avertissement_table = Table(empty_table_avertissement, colWidths=[80, 50], rowHeights=14)
    avertissement_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]))
    avertissement_table.wrapOn(c, -0.4 * inch, 1.1 * inch)
    avertissement_table.drawOn(c, -0.4 * inch, 1.1 * inch)

    # Tableau pour BLAME
    blame_table = Table(empty_table_blame, colWidths=[80, 50], rowHeights=13)
    blame_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]))
    blame_table.wrapOn(c, -0.4 * inch, 0.5 * inch)
    blame_table.drawOn(c, -0.4 * inch, 0.5 * inch)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(0*inch, 2.15*inch, "AVERTISSEMENT")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(0*inch, 0.95*inch, "BLAME")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0*inch, 0.3*inch, "Titulaire")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0*inch, -0.3*inch, classe.titulaire.admin.first_name + "  "+ classe.titulaire.admin.last_name )

    c.showPage()
    c.save()

    # Récupérer le contenu du buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Retourner le PDF en tant que réponse HTTP pour le téléchargement ou l'affichage
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{eleve.admin.first_name}_{eleve.admin.last_name}.pdf"'
    response.write(pdf)
    return response

def generate_bulletin_pdf(request, trimestre_id, eleve_id):
    eleve = get_object_or_404(Students, pk=eleve_id)
    trimestre = get_object_or_404(Periode, pk=trimestre_id)
    annee_scolaire = trimestre.annee_scolaire
    classe = eleve.classe_id
    
    # Obtenir toutes les périodes de l'année scolaire
    periodes = Periode.objects.filter(annee_scolaire=annee_scolaire).order_by('periode_name')

    
    classes_info = Classes.objects.annotate(nombre_eleves=Count('students')).select_related('titulaire__admin')
    # Trouver les informations de la classe de l'élève dans le résultat annoté
    classe_annotated_info = classes_info.filter(id=classe.id).first()

    if classe_annotated_info:
        effectif_classe = classe_annotated_info.nombre_eleves
    else:
        print("Classe non trouvée ou aucun effectif annoté pour cette classe")


    

    # Obtenir les notes et annoter les champs calculés
    notes = Note.objects.filter(eleve=eleve, trimestre=trimestre).annotate(
        moyenne_note=ExpressionWrapper(
            (((F('evaluation_classe') + F('devoir')) / 2) + F('composition')) / 2,
            output_field=DecimalField()
        ),
        moyenne_ponderee=ExpressionWrapper(
            (((F('evaluation_classe') + F('devoir')) / 2) + F('composition')) / 2 * F('coefficient'),
            output_field=DecimalField()
        )
    ).order_by('numero_matiere')

    # Mettre à jour le rang_matiere
    RangMatiere.objects.filter(
        eleve=eleve,
        matiere__in=notes.values('matiere'),
        periode=trimestre
    ).update(
        rang=Case(
            When(eleve=eleve, then=F('rang')),
            output_field=IntegerField()
        )
    )

    # Calculer les moyennes par période
    moyennes_par_periode = {}
    toutes_periodes_avant = True

    for periode in periodes:
        notes_pour_periode = notes.filter(trimestre=periode)
        if notes_pour_periode.exists():
            total_coefficients = notes_pour_periode.aggregate(total_coefficients=Sum('coefficient'))['total_coefficients'] or Decimal(0)
            total_pondered = notes_pour_periode.aggregate(total_pondered=Sum('moyenne_ponderee'))['total_pondered'] or Decimal(0)
            moyenne = total_pondered / total_coefficients if total_coefficients > 0 else None
            moyennes_par_periode[periode.periode_name] = moyenne
        else:
            moyennes_par_periode[periode.periode_name] = None
            toutes_periodes_avant = False

    # Calculer la moyenne annuelle si toutes les périodes ont des valeurs
    moyennes = Moyenne.objects.filter(eleve=eleve, periode__in=periodes)
    if toutes_periodes_avant:
        total_moyennes = moyennes.aggregate(total_moyennes=Sum('moyenne'))['total_moyennes'] or Decimal(0)
        moyenne_annuelle = total_moyennes / moyennes.count() if moyennes.count() > 0 else None
    else:
        moyenne_annuelle = None

    
    moyennes_par_categorie = {}
    for note in notes:
        categorie = note.matiere.categorie.nom
        if categorie not in moyennes_par_categorie:
            moyennes_par_categorie[categorie] = note.calculer_moyenne_categorie()
    
    moyennes_classe = Moyenne.objects.filter(eleve__classe_id=classe, periode=trimestre)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    
    moyenne_trimestre_obj = Moyenne.objects.get(eleve=eleve, periode=trimestre)
    moyenne_trimestre = moyenne_trimestre_obj.moyenne if moyenne_trimestre_obj else None
    rang_trimestre = moyenne_trimestre_obj.rang if moyenne_trimestre_obj else None

    
    
    # Créer un objet BytesIO pour stocker le PDF
    buffer = BytesIO()
    
    # Créer un canvas PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    c = my_temp(c)

    c.setStrokeColorRGB(0.1,0.8,0.1)
    c.setFillColorRGB(0,0,0)

    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(35, 8.1*inch, f"BULLETIN DE NOTES DU {trimestre.periode_name}")
    
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0, 7.8*inch, "Nom : " + eleve.admin.first_name) 
    c.drawString(0, 7.5*inch, "Prénom : " + eleve.admin.last_name)
    c.drawString(0, 7.2*inch, "Sexe : " + eleve.gender)
    c.drawString(80, 7.2*inch, "Statut : " + eleve.statut)
    c.drawString(200, 7.2*inch, "N° Matricule : " + eleve.numero_matricule)
    c.drawString(0, 6.9*inch, "Date de Naissance: " + eleve.date_naissance.strftime('%d-%b-%Y'))
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(4.8*inch, 9.0*inch, 'Année Scolaire: ' + f" {annee_scolaire}")
    table_classe = [
        ["CLASSE", "EFFECTIF"],
        [classe.classe_name, str(effectif_classe)],
        
    ]

    # Dessiner le tableau
    table = Table(table_classe, colWidths=[100, 60], rowHeights=14)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 12)
    ]))

    table.wrapOn(c, 4.8*inch, 8.5*inch,)
    table.drawOn(c, 4.8*inch, 8.5*inch,)
    
    # Récupérer le chemin de l'image de profil de l'élève
    image_path = settings.BASE_DIR + eleve.profile_pic.name
    # Vérifier si le fichier existe
    if not os.path.exists(image_path):
        raise OSError(f"Cannot open resource: {image_path}")
    
    if image_path:
        # Dessiner l'image sur le PDF
        c.drawImage(image_path, 5.5 * inch, 6.8 * inch, width=100, height=120)
    else:
        print("Image non trouvée")
    

    col_widths = [90, 50, 50, 50, 50, 30, 50,40,100, 80]

    # Convertir le HTML en tableau pour l'ajouter au PDF

    totals_row = [
    ['Totaux :', '', '', '', '', f'{total_coefficients}', f'{"{:.2f}".format(total_pondered)}']
    + [''] * 2  # Ajouter des colonnes vides pour compenser
    ]
    # Préparer les données pour le tableau des notes
    data = [['Matières', 'Notes de\n classe', 'Devoir', 'Compo', 'Moy', 'Coef', 'Notes', 'Rang', 'Observations', 'Prof chargé']]

    for note in notes:
        data.append([
            note.matiere.matiere_name, 
            'Inapte' if note.matiere.matiere_name=='EPS' and eleve.aptitude_sport=='Inapte' else note.evaluation_classe, 
            'Inapte' if note.matiere.matiere_name=='EPS' and eleve.aptitude_sport=='Inapte' else note.devoir, 
            'Inapte' if note.matiere.matiere_name=='EPS' and eleve.aptitude_sport=='Inapte' else note.composition, 
            '  ' if note.matiere.matiere_name=='EPS' and eleve.aptitude_sport=='Inapte' else "{:.2f}".format(note.moyenne_note),  # Formatage de la moyenne avec deux chiffres après la virgule
            note.coefficient, 
            "{:.2f}".format(note.moyenne_ponderee) if note.moyenne_ponderee is not None else ' ',  # Formatage de la moyenne pondérée avec deux chiffres après la virgule
            '  ' if note.matiere.matiere_name=='EPS' and eleve.aptitude_sport=='Inapte' else f"{note.rang_matiere}{'er' if note.rang_matiere == 1 and eleve.gender == 'M' else 'ère' if note.rang_matiere == 1 and eleve.gender == 'F' else 'ème'}", 
            'INAPTE' if note.matiere.matiere_name=='EPS' and eleve.aptitude_sport=='Inapte' else 'TRÈS FAIBLE' if note.moyenne_note < 5 else 
            'FAIBLE' if 5 <= note.moyenne_note < 7 else 
            'TRÈS INSUFFISANT' if 7 <= note.moyenne_note < 8 else 
            'INSUFFISANT' if 8 <= note.moyenne_note < 10 else 
            'PASSABLE' if 10 <= note.moyenne_note < 12 else 
            'ASSEZ BIEN' if 12 <= note.moyenne_note < 14 else 
            'BIEN' if 14 <= note.moyenne_note < 16 else 
            'TRÈS BIEN' if 16 <= note.moyenne_note < 18 else 
            'EXCELLENT' , 
            note.matiere.professeur_id.admin.first_name
        ])

    data.extend(totals_row)
    # Créer le tableau
    table = Table(data, colWidths=col_widths, rowHeights=None)
    # Appliquer un style au tableau
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    # Positionner le tableau sur le canevas
    table.wrapOn(c, 0, 0)
    table.drawOn(c, -60, 270)
    
    c.drawString(0 * inch, 3.2 * inch, f"Moyenne Générale du {trimestre.periode_name} : {moyenne_trimestre:.2f}" + "   " + f"Rang : {rang_trimestre}{'er' if rang_trimestre == 1 and eleve.gender == 'M' else 'ère' if rang_trimestre == 1 and eleve.gender == 'F' else 'ème'}")
    
    y_position = 2.6 * inch
    c.setFont("Helvetica-Bold", 9)
    y_position -= 0.5 * inch

    for periode_name, moyenne in moyennes_par_periode.items():
        if moyenne is None:
            c.drawString(-0.4 * inch, y_position, f"{periode_name}: ---")
        else:
            c.drawString(-0.4 * inch, y_position, f"{periode_name}: {moyenne:.2f}  Rang: ")
        y_position -= 0.2 * inch

    if moyenne_annuelle is not None:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(-0.4 * inch, y_position, f"Moyenne Annuelle : {moyenne_annuelle:.2f}      Rang: ")
        
    c.drawString(2.5 * inch, 2.1 * inch, f"Forte Moyenne de la classe : {moyenne_max:.2f}")
    c.drawString(2.5 * inch, 1.9 * inch, f"Faible Moyenne de la classe : {moyenne_min:.2f}")
    c.drawString(2.5 * inch, 1.7 * inch, f"Moyenne Générale de la classe : {moyenne_generale:.2f}")
    

    table_classe = [
        ["Catégorie Matière", "Moyenne"],
        
        
    ] 
    for categorie, moyenne in moyennes_par_categorie.items():
        table_classe.append([
            categorie,
            "{:.2f}".format(moyenne),
        ])

    # Dessiner le tableau
    table = Table(table_classe, colWidths=[200, 60], rowHeights=14)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 12)
    ]))
    
    table.wrapOn(c, -0.4 * inch, 2.3 * inch)
    table.drawOn(c, -0.4 * inch, 2.3 * inch)

    
    c.setFont("Helvetica-Bold", 14)

    c.drawString(1.8 * inch, 1 * inch, "Observations du conseil")
    c.drawString(1.8 * inch, 0.8 * inch, "______________________")
    c.drawString(1.8 * inch, 0.5 * inch, "______________________")

    c.setFont("Helvetica-Bold", 12)
    import locale
    from datetime import date

    #locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

    # Obtenir la date d'aujourd'hui
    dt = date.today().strftime("%d-%b-%Y")

    c.drawString(4.8 * inch, 1 * inch, "Sotouboua, le " + dt)

    c.setFont("Helvetica-Oblique", 12)
    c.drawString(5.3 * inch, 0.6 * inch, "Le Proviseur")
    

    # Tableau de disciplines et d'observations
    # table_disciplines = [
    #     ["FELICITATIONS", ""],
    #     ["ENCOURAGEMENTS", ""],
    #     ["TABLEAU D'HONNEUR", ""]
    # ]

    # # Dessiner le tableau
    # table = Table(table_disciplines, colWidths=[114, 40], rowHeights=14)
    # table.setStyle(TableStyle([
    #     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    #     ('GRID', (0, 0), (-1, -1), 1, colors.black),
    #     ('FONTSIZE', (0, 0), (-1, -1), 8)
    # ]))

    # table.wrapOn(c, -0.4 * inch, 2.3 * inch)
    # table.drawOn(c, -0.4 * inch, 2.3 * inch)

    # Les sections AVERTISSEMENT et BLAME (sans données)
    # Créer des tables vides pour ces sections

    empty_table_avertissement = [
        ["Absences", ""],
        ["Retards", ""],
        ["Travail", ""],
        ["Discipline", ""],
        ["Exclusions", ""],
    ]

    empty_table_blame = [
        ["Travail", ""],
        ["Discipline", ""],
    ]

    # Tableau pour AVERTISSEMENT
    avertissement_table = Table(empty_table_avertissement, colWidths=[50, 30], rowHeights=14)
    avertissement_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8)
    ]))
    avertissement_table.wrapOn(c, -0.4 * inch, 0.5 * inch)
    avertissement_table.drawOn(c, -0.4 * inch, 0.5 * inch)

    # Tableau pour BLAME
    blame_table = Table(empty_table_blame, colWidths=[50, 30], rowHeights=14)
    blame_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8)
    ]))
    blame_table.wrapOn(c, -0.4 * inch, 0.0 * inch)
    blame_table.drawOn(c, -0.4 * inch, 0.0 * inch)

    c.setFont("Helvetica-Bold", 8)
    c.drawString(0*inch, 1.5*inch, "AVERTISSEMENT")

    c.setFont("Helvetica-Bold", 8)
    c.drawString(0*inch, 0.4*inch, "BLAME")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0*inch, -0.2*inch, "Titulaire")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0*inch, -0.8*inch, classe.titulaire.admin.first_name + "  "+ classe.titulaire.admin.last_name )

    c.showPage()
    c.save()

    # Récupérer le contenu du buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Retourner le PDF en tant que réponse HTTP pour le téléchargement ou l'affichage
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{eleve.admin.first_name}_{eleve.admin.last_name}.pdf"'
    response.write(pdf)
    return response

def resultat_examen_pdf(request, examen_blanc_id):
    examen_blanc = get_object_or_404(ExamenBlanc, pk=examen_blanc_id)
    classe_concerne = examen_blanc.classes_concernees.all().first()
    matieres = Matieres.objects.filter(classe_id=classe_concerne)
    eleves = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc).order_by("rang")
    
    for matiere in matieres:
        matiere.possede_deja_notes = ExamenNote.objects.filter(matiere=matiere, examen=examen_blanc).exists()

    for numero_table_eleve in eleves:
        calculer_moyenne_examen(numero_table_eleve, examen_blanc)
        
    attribuer_rang_examen(examen_blanc)
    
    moyennes_classe = MoyenneExamen.objects.filter(examen=examen_blanc)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    
    # Annotation des élèves avec les moyennes des matières
    for eleve in eleves:
        eleve.moyennes_matieres = [
            eleve.examen_notes.filter(matiere=matiere, examen=examen_blanc).first()
            for matiere in matieres
        ]
        
    #eleves = sorted(eleves, key=lambda e: e.rang if e.rang is not None else float('inf'))
    #eleves = NumeroTableExamen.objects.filter(examen_blanc=examen_blanc).order_by("rang")
                    
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=20, bottomMargin=20)

    # Préparation des données pour le tableau
    table_data = []

    # En-têtes de colonnes
    headers = ['#', 'Numéro de table','NOM ET PRENOM']
    for matiere in matieres:
        headers.append(str(matiere.matiere_name))
    headers.extend(['Moyenne', 'Rang'])
    table_data.append(headers)

    # Ajout des données des élèves
    for index, eleve in enumerate(eleves, start=1):
        row = [str(index), f"{eleve.numero_table}", f"{eleve.student.admin.first_name} {eleve.student.admin.last_name}"]
        for moyenne_matiere in eleve.moyennes_matieres:
            if moyenne_matiere:
                moyenne = moyenne_matiere.note
            else:
                moyenne = 'N/A'
            row.append(f"{moyenne:.2f}" if isinstance(moyenne, float) else moyenne)
        row.append(f"{eleve.moyenne:.2f}" if eleve.moyenne is not None else 'N/A')
        row.append(
            f"{eleve.rang}er" if eleve.rang == 1 and eleve.student.gender == 'M' else
            f"{eleve.rang}ère" if eleve.rang == 1 and eleve.student.gender == 'F' else
            f"{eleve.rang}ème" if eleve.rang is not None else 'N/A'
        )
        table_data.append(row)

    # Création du tableau avec ReportLab
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9)
    ]))

    # Préparer les éléments à inclure dans le PDF
    elements = []

    styles = getSampleStyleSheet()

    # Titre et autres informations
    titre = Paragraph(f"RESULTATS  DU {examen_blanc.nom.upper()}", styles['Title'])
    elements.append(titre)
    elements.append(Spacer(1, 12))

    # Tableau des résultats
    elements.append(table)

    # Génération du PDF
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'resultat_{examen_blanc.nom}.pdf')

def resultat_classe_pdf(request, trimestre_id, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    trimestre_selected = get_object_or_404(Periode, pk=classe_id)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire)
    matieres = Matieres.objects.filter(classe_id=classe.id).order_by("matiere_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)
   
    print(trimestre_id)
    if trimestre_id:
        trimestre_selected = get_object_or_404(Periode, pk=trimestre_id)
    else:
        trimestre_selected = Periode.objects.filter(annee_scolaire=annee_scolaire).first()
    
    trimestre_nom = trimestre_selected.periode_name
    
    # Récupérer les moyennes et les rangs pour chaque élève pour le template
    for eleve in eleves:
        moyenne_trimestre_obj = Moyenne.objects.filter(
            eleve=eleve,
            periode=trimestre_selected
        ).first()
        if moyenne_trimestre_obj:
            eleve.moyenne_trimestre = moyenne_trimestre_obj.moyenne
            eleve.rang_trimestre = moyenne_trimestre_obj.rang
        else:
            eleve.moyenne_trimestre = None
            eleve.rang_trimestre = None
           
    # Annotation des élèves avec les moyennes des matières
    for eleve in eleves:
        eleve.moyennes_matieres = [
            eleve.rangs_matiere.filter(matiere=matiere, periode=trimestre_selected).first()
            for matiere in matieres
        ]
        
    eleves = sorted(eleves, key=lambda e: e.rang_trimestre if e.rang_trimestre is not None else float('inf'))
    
    # Calculer les statistiques par semestre pour la classe
    moyennes_classe = Moyenne.objects.filter(eleve__classe_id=classe, periode=trimestre_selected)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=20, bottomMargin=20)

    # Préparation des données pour le tableau
    table_data = []

    # En-têtes de colonnes
    headers = ['#', 'NOM ET PRENOM']
    for matiere in matieres:
        headers.append(str(matiere.matiere_name))
    headers.extend(['Moyenne', 'Rang'])
    table_data.append(headers)

    # Ajout des données des élèves
    for index, eleve in enumerate(eleves, start=1):
        row = [str(index), f"{eleve.admin.first_name} {eleve.admin.last_name}"]
        for moyenne_matiere in eleve.moyennes_matieres:
            if moyenne_matiere:
                moyenne = moyenne_matiere.moyenne_matiere
            else:
                moyenne = 'N/A'
            row.append(f"{moyenne:.2f}" if isinstance(moyenne, float) else moyenne)
        row.append(f"{eleve.moyenne_trimestre:.2f}" if eleve.moyenne_trimestre is not None else 'N/A')
        row.append(
            f"{eleve.rang_trimestre}er" if eleve.rang_trimestre == 1 and eleve.gender == 'M' else
            f"{eleve.rang_trimestre}ère" if eleve.rang_trimestre == 1 and eleve.gender == 'F' else
            f"{eleve.rang_trimestre}ème" if eleve.rang_trimestre is not None else 'N/A'
        )
        table_data.append(row)

    # Création du tableau avec ReportLab
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9)
    ]))

    # Préparer les éléments à inclure dans le PDF
    elements = []

    styles = getSampleStyleSheet()

    # Titre et autres informations
    titre = Paragraph(f"RESULTATS SCOLAIRES DU {trimestre_nom.upper()}<br/>{classe.classe_name}", styles['Title'])
    elements.append(titre)
    elements.append(Spacer(1, 12))

    # Tableau des résultats
    elements.append(table)

    # Génération du PDF
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='resultat_classe.pdf')

def attribuer_rang_annuel(classe, annee_scolaire):
    moyennes_annuelles = MoyenneAnnuelle.objects.filter(eleve__classe_id=classe, annee_scolaire=annee_scolaire).order_by('-moyenne')
    for index, moyenne_annuelle in enumerate(moyennes_annuelles):
        moyenne_annuelle.rang = index + 1
        moyenne_annuelle.save()

def resultat_annuel_classe(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire)
    matieres = Matieres.objects.filter(classe_id=classe.id).order_by("matiere_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)
    


     # Calculer les moyennes trimestrielles pour chaque élève
    for eleve in eleves:
        
        eleve.calculer_moyenne_annuelle(annee_scolaire)
    
    # Attribuer les rangs en fonction de la classe pour chaque période
    
    attribuer_rang_annuel(classe, annee_scolaire)
    
    # Récupérer les moyennes et les rangs pour chaque élève pour le template
    for eleve in eleves:
        moyenne_trimestre_obj = MoyenneAnnuelle.objects.filter(
            eleve=eleve,
            annee_scolaire=annee_scolaire
        ).first()
        if moyenne_trimestre_obj:
            eleve.moyenne_annuelle = moyenne_trimestre_obj.moyenne
            eleve.rang_annuel = moyenne_trimestre_obj.rang
        else:
            eleve.moyenne_annuelle = None
            eleve.rang_annuel = None
           
    # Annotation des élèves avec les moyennes des matières
    for eleve in eleves:
        eleve.moyenne_periodes = [Moyenne.objects.get(eleve=eleve, periode=periode) for periode in trimestres]
       
    moyennes_classe = MoyenneAnnuelle.objects.filter(eleve__classe_id=classe, annee_scolaire=annee_scolaire)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    nombre_moyennes = moyennes_classe.filter(moyenne__gte=10).count()
    
    
    return render(request, 'hod_template/view_annuel_classe_results.html', {
        'classe': classe,
        'eleves': eleves,
        'annee_scolaire':annee_scolaire,
        'matieres': matieres,
        'trimestres': trimestres,
        'moyenne_max':moyenne_max,
        'moyenne_min':moyenne_min,
        'moyenne_generale':moyenne_generale,
        'nombre_moyennes':nombre_moyennes,
    })

def resultat_annuel_classe_pdf(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire)
    matieres = Matieres.objects.filter(classe_id=classe.id).order_by("matiere_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)
    


     # Calculer les moyennes trimestrielles pour chaque élève
    for eleve in eleves:
        
        eleve.calculer_moyenne_annuelle(annee_scolaire)
    
    # Attribuer les rangs en fonction de la classe pour chaque période
    
    attribuer_rang_annuel(classe, annee_scolaire)
    
    # Récupérer les moyennes et les rangs pour chaque élève pour le template
    for eleve in eleves:
        moyenne_trimestre_obj = MoyenneAnnuelle.objects.filter(
            eleve=eleve,
            annee_scolaire=annee_scolaire
        ).first()
        if moyenne_trimestre_obj:
            eleve.moyenne_annuelle = moyenne_trimestre_obj.moyenne
            eleve.rang_annuel = moyenne_trimestre_obj.rang
        else:
            eleve.moyenne_annuelle = None
            eleve.rang_annuel = None
           
    # Annotation des élèves avec les moyennes des matières
    for eleve in eleves:
        eleve.moyenne_periodes = [Moyenne.objects.get(eleve=eleve, periode=periode) for periode in trimestres]
       
    moyennes_classe = MoyenneAnnuelle.objects.filter(eleve__classe_id=classe, annee_scolaire=annee_scolaire)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    nombre_moyennes = moyennes_classe.filter(moyenne__gte=10).count()
    
    
    # Créer une réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resultats_annuels_classe_{classe.classe_name}.pdf"'


    # Définir les marges
    margin_top = 20
    margin_bottom = 20
    margin_left = 30
    margin_right = 30

    # Créer un document PDF avec des marges ajustées
    pdf = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=margin_left,
        rightMargin=margin_right,
        topMargin=margin_top,
        bottomMargin=margin_bottom
    )
      
    # Créez un style personnalisé
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',  # Police en gras
        fontSize=14,                # Taille de la police
        leading=16,                 # Interligne
    )

    
    elements = []

    # Ajouter un titre
    styles = getSampleStyleSheet()
    title = Paragraph(f"Résultats annuels de la classe {classe.classe_name}", styles['Title'])
    elements.append(title)

    # Définir les données du tableau
    table_data = []

    # En-têtes de colonnes
    headers = ['NOM ET PRENOM', 'SEXE']
    for periode in trimestres:
        headers.append(str(periode.periode_name))
    headers.extend(['Moyenne Annuelle','Rang','Observation'])
    table_data.append(headers)
    #table_data = [["Nom", "Prénom", "Moyenne Semestre 1", "Moyenne Semestre 1", "Moyenne Semestre 2", "Moyenne Annuelle", "Rang Annuel"]]
    
    for eleve in eleves:
        row = [
            f"{eleve.admin.first_name}  {eleve.admin.last_name}",
            eleve.gender,
        ]
        for moyennes_periode in eleve.moyenne_periodes:
            moyennes_periode=moyennes_periode.moyenne if moyennes_periode else 'N/A'
            if isinstance(moyennes_periode, (float, decimal.Decimal)):
                formatted_moyenne = f"{float(moyennes_periode):.2f}"
            else:
                formatted_moyenne = moyennes_periode
            
            row.append(formatted_moyenne)
        row.append(f"{eleve.moyenne_annuelle:.2f}")
        row.append(
                f"{eleve.rang_annuel}er" if eleve.rang_annuel == 1 and eleve.gender == 'M' else
                f"{eleve.rang_annuel}ère" if eleve.rang_annuel == 1 and eleve.gender == 'F' else
                f"{eleve.rang_annuel}ème"
            )
        row.append('Passe')
        
        table_data.append(row)

    # Création du tableau avec ReportLab
    table = Table(table_data, repeatRows=1)

    # Appliquer un style au tableau
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9)
    ]))

    # Ajouter le tableau aux éléments du document
    elements.append(table)
    
    
    elements.append(Paragraph("   "))
      
    # Ajoutez les Paragraphs avec le style personnalisé
    elements.append(Paragraph(f"Moyenne Anuelle la plus forte de la classe: {moyenne_max:.2f}", custom_style))
    elements.append(Paragraph(f"Moyenne Anuelle la plus faible de la classe: {moyenne_min:.2f}", custom_style))
    elements.append(Paragraph(f"Moyenne Anuelle générale de la classe: {moyenne_generale:.2f}", custom_style))


    # Construire le document PDF
    pdf.build(elements)

    return response

def my_temp(c):
    # Utilisation du format A4
    width, height = A4
    
    # Chemin de l'image d'arrière-plan
    background_image_path = finders.find('dist/img/logo.jpg')
    
    # Dessiner l'image d'arrière-plan
    background_image = ImageReader(background_image_path)
    c.drawImage(background_image, 0, 0, width=width, height=height,preserveAspectRatio=True)
    
    # Dessiner un rectangle semi-transparent par-dessus l'image pour simuler une réduction d'opacité
    c.setFillColorRGB(1, 1, 1)  # Couleur blanche pour le rectangle
    c.setFillAlpha(0.9)  # Opacité du rectangle
    c.rect(0, 0, width, height, fill=1, stroke=0)


    c.translate(inch, inch)
    # Définir une police de grande taille
    c.setFont("Helvetica", 6)

    c.setFillColorRGB(0, 0, 0)     
    # Texte et autres éléments
    c.drawString(-50, 9.5*inch, "MINISTERE DES ENSEIGNEMENTS PRIMAIRE, SECONDAIRE ET TECHNIQUE")
    
    c.setFont("Helvetica-Bold", 8)
    c.line(0.3*inch, 9.4*inch, 1.5*inch, 9.4*inch)

    c.drawString(-50, 9.2*inch, "DIRECTION REGIONALE DE L'EDUCATION, CENTRALE")
    
    c.line(0.3*inch, 9.1*inch, 1.5*inch, 9.1*inch)

    c.setFont("Helvetica", 6)
    c.drawString(-50, 8.9*inch, "INSPECTION DE L'ENSEIGNEMENT SECONDAIRE GENERAL DE SOTOUBOUA")

    c.line(0.3*inch, 8.7*inch, 1.5*inch, 8.7*inch)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(-5, 8.5*inch, "LYCÉE DE SOTOUBOUA")
    
    # Choix des couleurs
    c.setStrokeColorRGB(0.1, 0.8, 0.1)
    
    image_path = finders.find('dist/img/logo.jpg')
    c.drawImage(image_path, 2.6*inch, 8.3*inch, width=100, height=120)
    
    c.setFillColorRGB(0, 0, 0)  # Couleur de la police
    c.drawString(4.6*inch, 9.5*inch, 'REPUBLIQUE TOGOLAISE')
    c.drawString(4.8*inch, 9.3*inch, 'Travail - Liberté - Patrie')

    c.line(6.1*inch, 9.2*inch, 5.1*inch, 9.2*inch)

    from datetime import date
    dt = date.today().strftime("%d-%b-%Y")
    
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(1, 0, 0)  # Couleur de la police
    c.drawString(0, -0.9*inch, u"\u00A9"+" mangamanawezou@gmail.com")
    c.rotate(45)
    c.setFillColorCMYK(0, 0, 0, 0.08)  # Couleur de la police
    c.setFont("Helvetica", 100)
    c.drawString(2*inch, 1*inch, "LYSOTO")
    c.rotate(-45)

    return c

#======================================
def generate_student_card_pdf(request, student_id):
    student = get_object_or_404(Students, id=student_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Informations de la carte
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Carte Scolaire")

    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Nom: {student.admin.last_name}")
    p.drawString(100, 750, f"Prénom: {student.admin.first_name}")
    p.drawString(100, 730, f"Matricule: {student.numero_matricule}")
    p.drawString(100, 710, f"Date de Naissance: {student.date_naissance.strftime('%d/%m/%Y')}")
    p.drawString(100, 690, f"Adresse: {student.address}")
    p.drawString(100, 670, f"Contact Parent: {student.contact_parent}")
    p.drawString(100, 650, f"Aptitude Sportive: {student.aptitude_sport}")

    # Ajouter la photo de profil
    if student.profile_pic:
        profile_pic_path = settings.BASE_DIR + student.profile_pic.name
        profile_pic_full_path = default_storage.path(profile_pic_path)
        p.drawImage(profile_pic_full_path, 400, 700, width=100, height=100)

    # Ajouter le QR code
    if student.qr_code:
        qr_code_path = student.qr_code.name
        qr_code_full_path = default_storage.path(qr_code_path)
        p.drawImage(qr_code_full_path, 100, 550, width=100, height=100)

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def generate_class_student_cards_pdf(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    
    # Récupérer l'année scolaire sélectionnée, sinon l'année en cours
    annee_scolaire_id = request.GET.get('annee_scolaire', None)
    
    if annee_scolaire_id:
        annee_scolaire = get_object_or_404(SessionYearModel, pk=annee_scolaire_id)
    else:
        annee_scolaire = SessionYearModel.objects.filter(is_complete=False).first()
    
    students = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire).order_by('admin__first_name')
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    width, height = A4
    card_width = width / 2 
    card_height = height / 4 
    
    x_offset = 0
    y_offset = height - card_height - 0
    
    cards_per_page = 8
    student_count = 0
    
    for student in students:
        # Nouvelle page après chaque groupe de 8 cartes
        if student_count % cards_per_page == 0 and student_count > 0:
            p.showPage()  # Passer à la page suivante
            x_offset = 0
            y_offset = height - card_height  # Réinitialiser les offsets pour la nouvelle page

        # Positionner les cartes (2 par ligne)
        if student_count % 2 == 0:
            x_offset = 0  # Colonne gauche
            if student_count > 0 and student_count % 8 != 0:  # Ne réduire y_offset que pour les cartes suivantes après la première
                y_offset -= card_height  # Passer à la ligne suivante après deux cartes
        else:
            x_offset = card_width  # Colonne droite
        
        # Dessiner la carte
        
        # Chemin de l'image d'arrière-plan
        background_image_path = finders.find('dist/img/logo.jpg')
        
        # Dessiner l'image d'arrière-plan
        background_image = ImageReader(background_image_path)
        p.drawImage(background_image, x_offset, y_offset, width=card_width, height=card_height,preserveAspectRatio=True)
        
        # Dessiner un rectangle semi-transparent par-dessus l'image pour simuler une réduction d'opacité
        p.setFillColorRGB(1, 1, 1)  # Couleur blanche pour le rectangle
        p.setFillAlpha(0.9)  # Opacité du rectangle
        p.rect(x_offset, y_offset, card_width, card_height, stroke=1, fill=1)
        
        image_path = finders.find('dist/img/Le-drapeau-du-Togo.jpg')
        p.drawImage(image_path, x_offset + 10, y_offset + card_height - 40, width=50, height=30)
        
        image_path = finders.find('dist/img/RT.png')
        p.drawImage(image_path, x_offset + 240, y_offset + card_height - 40, width=40, height=30)
        
        # Ajouter les informations de l'élève
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x_offset + 80, y_offset + card_height - 20, "REPUBLIQUE TOGOLAISE")
        p.setFillColorRGB(0, 0, 1)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(x_offset + 105, y_offset + card_height - 30, "Lycée de Sotouboua")
        p.setFillColorRGB(1, 0, 0)
        p.setFont("Helvetica-Bold", 11.5)
        p.drawString(x_offset + 90, y_offset + card_height - 40, "Carte d' Identité Scolaire")
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica", 6)
        #p.linearGradient(x_offset + 10, y_offset + card_height - 50, x_offset + 200, y_offset + card_height - 50, colors)
        p.line(x_offset + 50, y_offset + card_height - 45, x_offset + 250, y_offset + card_height - 45)
        p.setFont("Helvetica", 11)
        p.setFillColorRGB(0.5, 0, 0.5)
        p.drawString(x_offset + 40, y_offset + card_height - 60, f"Année Scolaire: {student.annee_scolaire.nom}")
        p.setFont("Helvetica", 8)
        p.setFillColorRGB(0, 0, 0)
        p.drawString(x_offset + 10, y_offset + card_height - 70, f"Je soussigné : {student.admin.last_name} ")
        p.setFont("Helvetica", 10)
        p.drawString(x_offset + 10, y_offset + card_height - 80, f"Nom: {student.admin.first_name}")
        p.drawString(x_offset + 10, y_offset + card_height - 90, f"Prénom: {student.admin.last_name}")
        p.drawString(x_offset + 10, y_offset + card_height - 100, f"Matricule: {student.numero_matricule}")
        p.drawString(x_offset + 100, y_offset + card_height - 100, f"Sexe: {student.gender}")
        p.drawString(x_offset + 10, y_offset + card_height - 110, f"Classe: {student.classe_id.classe_name}")
        p.drawString(x_offset + 100, y_offset + card_height - 110, f"Sport: {student.aptitude_sport}")
        p.drawString(x_offset + 10, y_offset + card_height - 120, f"Date de Naissance: {student.date_naissance.strftime('%d/%m/%Y')}")
        p.drawString(x_offset + 10, y_offset + card_height - 130, f"Adresse: {student.address}")
        p.drawString(x_offset + 10, y_offset + card_height - 140, f"Contact Parent: {student.contact_parent}")
        
        # Ajouter la photo de profil
        if student.profile_pic:
            profile_pic_path = settings.BASE_DIR + student.profile_pic.name
            profile_pic_full_path = default_storage.path(profile_pic_path)
            p.drawImage(profile_pic_full_path, x_offset + card_width - 110, y_offset + card_height - 150, width=100, height=100)
        
        # Ajouter le QR code
        if student.qr_code:
            qr_code_full_path = default_storage.path(student.qr_code.name)
            p.drawImage(qr_code_full_path, x_offset + 10, y_offset + 0, width=60, height=60)
        
        student_count += 1
    
    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def enregistrer_comportement1(request, student_id):
    student = get_object_or_404(Students, id=student_id)

    if request.method == 'POST':
        aspect = request.POST.get('aspect')
        points = int(request.POST.get('points'))
        periode = request.POST.get('periode')
        comportement = Comportement(aspect=aspect, points=points, student=student, periode=periode, date=datetime.date.today())
        comportement.save()
        return redirect('liste_eleves')  # Remplacez par l'URL appropriée

    return render(request, 'hod_template/enregistrer_comportement.html', {'student': student})

def enregistrer_comportement(request, student_id):
    student = get_object_or_404(Students, id=student_id)
    classe_id=student.classe_id
    periode = Periode.objects.filter(annee_scolaire=SessionYearModel.get_current_session()).first()
    
    if request.method == 'POST':
        aspect = request.POST.get('aspect')
        comportement = Comportement(aspect=aspect, student=student, periode=periode, date=datetime.date.today())
        comportement.save()
        messages.success(request, "L'Aspect a été ajoutée avec succès.")
        return redirect('show-classe', classe_id=classe_id.id)

    return redirect('show-classe', classe_id=classe_id.id)

def scanner_qr_code(request, student_id):
    student = get_object_or_404(Students, id=student_id)
    
    # Supposez que vous utilisez une bibliothèque pour lire le QR code côté client et envoyer les données
    # Traitement pour lire les données du QR code
    
    # Ajoutez les points pour le comportement basé sur le QR code scanné
    comportement = Comportement(aspect='engagement', points=5, student=student, periode=Periode.objects.first(), date=datetime.date.today())
    comportement.save()

    return JsonResponse({'status': 'success'})

def afficher_points(request, student_id):
    student = get_object_or_404(Students, id=student_id)
    periode = Periode.objects.filter(annee_scolaire=SessionYearModel.get_current_session()).first()
    points_totaux_periode = periode.calculer_points_totaux()
    points_totaux_annee = student.annee_scolaire.calculer_points_totaux()

    return render(request, 'hod_template/afficher_points.html', {
        'student': student,
        'points_totaux_periode': points_totaux_periode,
        'points_totaux_annee': points_totaux_annee,
    })


def generate_statistics_for_matiere(matiere, trimestre):
    notes_matiere = Note.objects.filter(matiere=matiere, trimestre=trimestre)
    effectif_classe = notes_matiere.count()
    if effectif_classe == 0:
        return None

    note_minimale = notes_matiere.aggregate(min_note=Min('moyenne_matiere'))['min_note']
    moyenne_classe = notes_matiere.aggregate(avg_note=Avg('moyenne_matiere'))['avg_note']
    note_maximale = notes_matiere.aggregate(max_note=Max('moyenne_matiere'))['max_note']
    nombre_eleves_moyenne_sup_10 = notes_matiere.filter(moyenne_matiere__gte=10).count()
    
    

    intervalles_count = [
        notes_matiere.filter(moyenne_matiere__gte=0, moyenne_matiere__lt=6).count(),
        notes_matiere.filter(moyenne_matiere__gte=6, moyenne_matiere__lt=10).count(),
        notes_matiere.filter(moyenne_matiere__gte=10, moyenne_matiere__lt=15).count(),
        notes_matiere.filter(moyenne_matiere__range=(15, 20)).count()
    ]
    notes_matiere.filter(
        Q(moyenne_matiere__lt=0) | 
        Q(moyenne_matiere__gte=20) | 
        (Q(moyenne_matiere__gte=6) & Q(moyenne_matiere__lt=10)) | 
        (Q(moyenne_matiere__gte=15) & Q(moyenne_matiere__lte=20))
    ).count()


    # Calcul des pourcentages
    total_notes = effectif_classe
    pourcentages = [count / total_notes * 100 for count in intervalles_count]
    
    pourcentage_moyenne = (nombre_eleves_moyenne_sup_10/ effectif_classe) * 100

    return {
        'effectif_classe': effectif_classe,
        'note_minimale': note_minimale,
        'note_maximale': note_maximale,
        'nombre_eleves_moyenne_sup_10': nombre_eleves_moyenne_sup_10,
        'pourcentage_moyenne': pourcentage_moyenne,
        'moyenne_classe': moyenne_classe,
        'intervalles_count': intervalles_count,
        'pourcentages': pourcentages
    }


def generate_table_for_matiere_statistics(matiere, trimestre):
    statistics = generate_statistics_for_matiere(matiere, trimestre)
    if statistics is None:
        return None

    table_data = [matiere.matiere_name, str(statistics['nombre_eleves_moyenne_sup_10']), f"{statistics['pourcentage_moyenne']:.2f}%", str(statistics['note_minimale']), f"{statistics['note_maximale']:.2f}", f"{statistics['moyenne_classe']:.2f}", \
        str(statistics['intervalles_count'][0]), f"{statistics['pourcentages'][0]:.2f}%", str(statistics['intervalles_count'][1]), f"{statistics['pourcentages'][1]:.2f}%", str(statistics['intervalles_count'][2]), \
              f"{statistics['pourcentages'][2]:.2f}%",str(statistics['intervalles_count'][3]), f"{statistics['pourcentages'][3]:.2f}%"] 
    
    #return table_data, table_style
    return table_data

def statistique_classe_pdf(request, trimestre_id,classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    trimestre_selected = get_object_or_404(Periode, pk=classe_id)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire)
    matieres = Matieres.objects.filter(classe_id=classe.id).order_by("matiere_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)
   
    print(trimestre_id)
    if trimestre_id:
        trimestre_selected = get_object_or_404(Periode, pk=trimestre_id)
    else:
        trimestre_selected = Periode.objects.filter(annee_scolaire=annee_scolaire).first()
    
    trimestre_nom = trimestre_selected.periode_name
    
    # Récupérer les moyennes et les rangs pour chaque élève pour le template
    for eleve in eleves:
        moyenne_trimestre_obj = Moyenne.objects.filter(
            eleve=eleve,
            periode=trimestre_selected
        ).first()
        if moyenne_trimestre_obj:
            eleve.moyenne_trimestre = moyenne_trimestre_obj.moyenne
            eleve.rang_trimestre = moyenne_trimestre_obj.rang
        else:
            eleve.moyenne_trimestre = None
            eleve.rang_trimestre = None
           
    # Annotation des élèves avec les moyennes des matières
    for eleve in eleves:
        eleve.moyennes_matieres = [
            eleve.rangs_matiere.filter(matiere=matiere, periode=trimestre_selected).first()
            for matiere in matieres
        ]
        
    eleves = sorted(eleves, key=lambda e: e.rang_trimestre if e.rang_trimestre is not None else float('inf'))
    
    # Calculer les statistiques par semestre pour la classe
    moyennes_classe = Moyenne.objects.filter(eleve__classe_id=classe, periode=trimestre_selected)
    moyenne_max = moyennes_classe.aggregate(Max('moyenne'))['moyenne__max']
    moyenne_min = moyennes_classe.aggregate(Min('moyenne'))['moyenne__min']
    moyenne_generale = moyennes_classe.aggregate(Avg('moyenne'))['moyenne__avg']
    nombre_eleves_moyenne_sup_10 = moyennes_classe.filter(moyenne__gte=10).count()
    
     # Calculez le pourcentage
    total_eleves = moyennes_classe.count()
    pourcentage_moyenne_sup_10 = (nombre_eleves_moyenne_sup_10 / total_eleves) * 100
        # Filtrer les élèves par sexe
    eleves_hommes = moyennes_classe.filter(eleve__gender='M')
    eleves_femmes = moyennes_classe.filter(eleve__gender='F')

    # Filtrer les élèves par sexe ayant une moyenne semestrielle supérieure ou égale à 10
    eleves_moyenne_sup_10_hommes = eleves_hommes.filter(moyenne__gte=10)
    eleves_moyenne_sup_10_femmes = eleves_femmes.filter(moyenne__gte=10)

    # Comptez le nombre d'élèves par sexe avec une moyenne semestrielle supérieure ou égale à 10
    nombre_eleves_moyenne_sup_10_hommes = eleves_moyenne_sup_10_hommes.count()
    nombre_eleves_moyenne_sup_10_femmes = eleves_moyenne_sup_10_femmes.count()

    # Calculez le pourcentage par sexe
    total_hommes = eleves_hommes.count()
    total_femmes = eleves_femmes.count()
    if total_femmes != 0:
        total_femmes = total_femmes
    else:
        total_femmes = 1
    pourcentage_moyenne_sup_10_hommes = (nombre_eleves_moyenne_sup_10_hommes / total_hommes) * 100
    pourcentage_moyenne_sup_10_femmes = (nombre_eleves_moyenne_sup_10_femmes / total_femmes) * 100
    
        # Filtrer les élèves avec une moyenne semestrielle entre 9 et 10
    eleves_notes_entre_9_et_10 = moyennes_classe.filter(moyenne__range=[9, 10])

    # Comptez le nombre total d'élèves avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_9_et_10 = eleves_notes_entre_9_et_10.count()
    
    # Calculez le pourcentage par sexe pour les notes entre 9 et 10
    pourcentage_notes_entre_9_et_10 = (nombre_eleves_notes_entre_9_et_10 / total_eleves) * 100

        # Filtrer les élèves par sexe ayant une moyenne semestrielle entre 9 et 10
    eleves_notes_entre_9_et_10_hommes = eleves_hommes.filter(moyenne__range=[9, 10])
    eleves_notes_entre_9_et_10_femmes = eleves_femmes.filter(moyenne__range=[9, 10])

    # Comptez le nombre d'élèves par sexe avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_9_et_10_hommes = eleves_notes_entre_9_et_10_hommes.count()
    nombre_eleves_notes_entre_9_et_10_femmes = eleves_notes_entre_9_et_10_femmes.count()

    # Calculez le pourcentage par sexe
    pourcentage_notes_entre_9_et_10_hommes = (nombre_eleves_notes_entre_9_et_10_hommes / total_hommes) * 100
    if total_femmes != 0:
        pourcentage_notes_entre_9_et_10_femmes = (nombre_eleves_notes_entre_9_et_10_femmes / total_femmes) * 100
    else:
        pourcentage_notes_entre_9_et_10_femmes = 0
        
        # Filtrer les élèves avec une moyenne semestrielle entre 8 et 9
    eleves_notes_entre_8_et_9 = moyennes_classe.filter(moyenne__range=[8, 9])

    # Comptez le nombre total d'élèves avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_8_et_9 = eleves_notes_entre_8_et_9.count()
    
    # Calculez le pourcentage par sexe pour les notes entre 9 et 10
    pourcentage_notes_entre_8_et_9 = (nombre_eleves_notes_entre_8_et_9 / total_eleves) * 100

        # Filtrer les élèves par sexe ayant une moyenne semestrielle entre 9 et 10
    eleves_notes_entre_8_et_9_hommes = eleves_hommes.filter(moyenne__range=[8, 9])
    eleves_notes_entre_8_et_9_femmes = eleves_femmes.filter(moyenne__range=[8, 9])

    # Comptez le nombre d'élèves par sexe avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_8_et_9_hommes = eleves_notes_entre_8_et_9_hommes.count()
    nombre_eleves_notes_entre_8_et_9_femmes = eleves_notes_entre_8_et_9_femmes.count()

    # Calculez le pourcentage par sexe
    pourcentage_notes_entre_8_et_9_hommes = (nombre_eleves_notes_entre_8_et_9_hommes / total_hommes) * 100
    if total_femmes != 0:
        pourcentage_notes_entre_8_et_9_femmes = (nombre_eleves_notes_entre_8_et_9_femmes / total_femmes) * 100
    else:
        pourcentage_notes_entre_8_et_9_femmes = 0
        
        # Filtrer les élèves avec une moyenne semestrielle entre 7 et 8
    eleves_notes_entre_7_et_8 = moyennes_classe.filter(moyenne__range=[7, 8])

    # Comptez le nombre total d'élèves avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_7_et_8 = eleves_notes_entre_7_et_8.count()
    
    # Calculez le pourcentage par sexe pour les notes entre 9 et 10
    pourcentage_notes_entre_7_et_8 = (nombre_eleves_notes_entre_7_et_8 / total_eleves) * 100

        # Filtrer les élèves par sexe ayant une moyenne semestrielle entre 9 et 10
    eleves_notes_entre_7_et_8_hommes = eleves_hommes.filter(moyenne__range=[7, 8])
    eleves_notes_entre_7_et_8_femmes = eleves_femmes.filter(moyenne__range=[7, 8])

    # Comptez le nombre d'élèves par sexe avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_7_et_8_hommes = eleves_notes_entre_7_et_8_hommes.count()
    nombre_eleves_notes_entre_7_et_8_femmes = eleves_notes_entre_7_et_8_femmes.count()

    # Calculez le pourcentage par sexe
    pourcentage_notes_entre_7_et_8_hommes = (nombre_eleves_notes_entre_7_et_8_hommes / total_hommes) * 100
    if total_femmes != 0:
        pourcentage_notes_entre_7_et_8_femmes = (nombre_eleves_notes_entre_7_et_8_femmes / total_femmes) * 100
    else:
        pourcentage_notes_entre_7_et_8_femmes = 0
        
        # Filtrer les élèves avec une moyenne semestrielle entre 6 et 7
    eleves_notes_entre_6_et_7 = moyennes_classe.filter(moyenne__range=[6, 7])

    # Comptez le nombre total d'élèves avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_6_et_7 = eleves_notes_entre_6_et_7.count()
    
    # Calculez le pourcentage par sexe pour les notes entre 9 et 10
    pourcentage_notes_entre_6_et_7 = (nombre_eleves_notes_entre_6_et_7 / total_eleves) * 100

        # Filtrer les élèves par sexe ayant une moyenne semestrielle entre 9 et 10
    eleves_notes_entre_6_et_7_hommes = eleves_hommes.filter(moyenne__range=[6, 7])
    eleves_notes_entre_6_et_7_femmes = eleves_femmes.filter(moyenne__range=[6, 7])

    # Comptez le nombre d'élèves par sexe avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_6_et_7_hommes = eleves_notes_entre_6_et_7_hommes.count()
    nombre_eleves_notes_entre_6_et_7_femmes = eleves_notes_entre_6_et_7_femmes.count()

    # Calculez le pourcentage par sexe
    pourcentage_notes_entre_6_et_7_hommes = (nombre_eleves_notes_entre_6_et_7_hommes / total_hommes) * 100
    if total_femmes != 0:
        pourcentage_notes_entre_6_et_7_femmes = (nombre_eleves_notes_entre_6_et_7_femmes / total_femmes) * 100
    else:
        pourcentage_notes_entre_6_et_7_femmes = 0
        
        # Filtrer les élèves avec une moyenne semestrielle entre 0 et 6
    eleves_notes_entre_0_et_6 = moyennes_classe.filter(moyenne__range=[0, 6])

    # Comptez le nombre total d'élèves avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_0_et_6 = eleves_notes_entre_0_et_6.count()
    
    # Calculez le pourcentage par sexe pour les notes entre 9 et 10
    pourcentage_notes_entre_0_et_6 = (nombre_eleves_notes_entre_0_et_6 / total_eleves) * 100

        # Filtrer les élèves par sexe ayant une moyenne semestrielle entre 9 et 10
    eleves_notes_entre_0_et_6_hommes = eleves_hommes.filter(moyenne__range=[0, 6])
    eleves_notes_entre_0_et_6_femmes = eleves_femmes.filter(moyenne__range=[0, 6])

    # Comptez le nombre d'élèves par sexe avec une moyenne semestrielle entre 9 et 10
    nombre_eleves_notes_entre_0_et_6_hommes = eleves_notes_entre_0_et_6_hommes.count()
    nombre_eleves_notes_entre_0_et_6_femmes = eleves_notes_entre_0_et_6_femmes.count()

    # Calculez le pourcentage par sexe
    pourcentage_notes_entre_0_et_6_hommes = (nombre_eleves_notes_entre_0_et_6_hommes / total_hommes) * 100
    if total_femmes != 0:
        pourcentage_notes_entre_0_et_6_femmes = (nombre_eleves_notes_entre_0_et_6_femmes / total_femmes) * 100
    else:
        pourcentage_notes_entre_0_et_6_femmes = 0

    
   
    eleves_classe = classe.students.all()

           
    # Récupérer les informations sur les classes avec le décompte des élèves
    classes_info = Classes.objects.annotate(nombre_eleves=Count('students')).prefetch_related('titulaire__admin')
    #classes_info = Classes.objects.annotate(nombre_eleves=Count('students')).select_related('titulaire__admin').order_by('classe_name')


    
    # Trouver les informations de la classe de l'élève dans le résultat annoté
    classe_annotated_info = classes_info.filter(id=classe.id).first()

    if classe_annotated_info:
        effectif_classe = classe_annotated_info.nombre_eleves
        print(f"L'effectif de la classe de l'élève est de : {effectif_classe}")
    else:
        print("Classe non trouvée ou aucun effectif annoté pour cette classe")



    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=20, bottomMargin=20)

   

    
    # ... (votre code existant)
    table_data = []
    intervalle_notes = ["[10; 20]", "[9; 10[", "[8; 9[", "[7; 8[", "[6; 7[", "[0; 6["]

    # En-têtes de colonnes
    headers = ['#','Intervalle de Notes', "Nbre d'élèves", "Pourcentage","Nbre de Garçons", "Pourcentage de Garçons", "Nbre de Filles", "Pourcentage de Filles"]
    
    table_data.append(headers)

    rows=[['1',"[10;    20]", nombre_eleves_moyenne_sup_10, f"{pourcentage_moyenne_sup_10:.2f}%", nombre_eleves_moyenne_sup_10_hommes, \
        f"{pourcentage_moyenne_sup_10_hommes:.2f}%", nombre_eleves_moyenne_sup_10_femmes, f"{pourcentage_moyenne_sup_10_femmes:.2f}%"],
         ['2',"[9;      10[", nombre_eleves_notes_entre_9_et_10, f"{pourcentage_notes_entre_9_et_10:.2f}%", nombre_eleves_notes_entre_9_et_10_hommes, \
        f"{pourcentage_notes_entre_9_et_10_hommes:.2f}%", nombre_eleves_notes_entre_9_et_10_femmes, f"{pourcentage_notes_entre_9_et_10_femmes:.2f}%"],
         ['3',"[8;       9[", nombre_eleves_notes_entre_8_et_9, f"{pourcentage_notes_entre_8_et_9:.2f}%", nombre_eleves_notes_entre_8_et_9_hommes, \
        f"{pourcentage_notes_entre_8_et_9_hommes:.2f}%", nombre_eleves_notes_entre_8_et_9_femmes, f"{pourcentage_notes_entre_8_et_9_femmes:.2f}%"],
         ['4',"[7;       8[", nombre_eleves_notes_entre_7_et_8, f"{pourcentage_notes_entre_7_et_8:.2f}%", nombre_eleves_notes_entre_7_et_8_hommes, \
        f"{pourcentage_notes_entre_7_et_8_hommes:.2f}%", nombre_eleves_notes_entre_7_et_8_femmes, f"{pourcentage_notes_entre_7_et_8_femmes:.2f}%"],
         ['5',"[6;       7[", nombre_eleves_notes_entre_6_et_7, f"{pourcentage_notes_entre_6_et_7:.2f}%", nombre_eleves_notes_entre_6_et_7_hommes, \
        f"{pourcentage_notes_entre_6_et_7_hommes:.2f}%", nombre_eleves_notes_entre_6_et_7_femmes, f"{pourcentage_notes_entre_6_et_7_femmes:.2f}%"],
         ['6',"[0;       6[", nombre_eleves_notes_entre_0_et_6, f"{pourcentage_notes_entre_0_et_6:.2f}%", nombre_eleves_notes_entre_0_et_6_hommes, \
        f"{pourcentage_notes_entre_0_et_6_hommes:.2f}%", nombre_eleves_notes_entre_0_et_6_femmes, f"{pourcentage_notes_entre_0_et_6_femmes:.2f}%"],
         
         ]
    for row in rows:
        table_data.append(row)
    
    

    # Création du tableau avec ReportLab
    table = Table(table_data, repeatRows=1)

    # Appliquer un style au tableau
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 11)
    ]))

    styles = getSampleStyleSheet()

    # Ajoutez le tableau à la liste d'éléments
    # Liste pour contenir les éléments à ajouter au document
    elements = []

    heading_style = getSampleStyleSheet()['Heading1']
    heading_style.alignment = 1  # 0=Left, 1=Center, 2=Right
    elements.append(Paragraph("LYCÉE DE SOTOUBOUA", heading_style))
    title_style = getSampleStyleSheet()['Heading2']
    title_style.alignment = 1
    elements.append(Paragraph(f"STATISTIQUE de la classe de  {classe.classe_name} du {trimestre_nom}", title_style))
    
    title_style = getSampleStyleSheet()['Heading3']
    title_style.alignment = 0
    elements.append(Paragraph(f"Effectif: {effectif_classe} ", title_style))
    

    elements.append(table)
    
    # Générer le pied de page du document PDF
    footing_style = getSampleStyleSheet()['Heading3']
    footing_style.alignment = 1

    elements.append(Paragraph("   ", footing_style))

    heading_style = styles['Heading2']
    elements.append(Paragraph("Statistiques par Matière:", heading_style))
    
    # Générer les tables de statistiques pour chaque matière
    matiere_table_data = []
    headers = ['Matière', 'Nbre de \n Moyenne', 'Pourcentage','Note min', 'Note Max', 'Moy', 'Notes \n (0-6)', 'Pourcentage\n(0-6)', 'Notes \n (6-10)',  
             'Pourcentage\n (6-10)', 'Notes\n (10-15)', 'Pourcentage\n (10-15)','Notes\n (15-20)', 'Pourcentage \n(15-20)']
    matiere_table_data.append(headers)

    matiere_tables = []
    for matiere in matieres:
        table = generate_table_for_matiere_statistics(matiere, trimestre_selected)
        if table:
            matiere_tables.append(table)

    # Ajoutez chaque ligne de données au tableau principal
    for table in matiere_tables:
        matiere_table_data.append(table)

    # Création du tableau avec ReportLab
    matiere_table = Table(matiere_table_data, repeatRows=1, rowHeights=None)

    # Appliquer un style au tableau
    matiere_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9)
    ]))

    elements.append(matiere_table)


    
    
    
    # Ajoutez les éléments à chaque page
    doc.build(elements)

    # Obtenez le PDF généré à partir du tampon
    pdf = buffer.getvalue()
    buffer.close()

    # Utilisez le contenu du PDF comme réponse HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Résultats_de_{classe.classe_name}.pdf"'
    return response


def generate_graphique_pdf(request, trimestre_id, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    trimestre_selected = get_object_or_404(Periode, pk=classe_id)
    annee_scolaire = SessionYearModel.get_current_session()
    eleves = Students.objects.filter(classe_id=classe, annee_scolaire=annee_scolaire)
    matieres = Matieres.objects.filter(classe_id=classe.id).order_by("matiere_name")
    trimestres = Periode.objects.filter(annee_scolaire=annee_scolaire)
   
    if trimestre_id:
        trimestre_selected = get_object_or_404(Periode, pk=trimestre_id)
    else:
        trimestre_selected = Periode.objects.filter(annee_scolaire=annee_scolaire).first()
    
    trimestre_nom = trimestre_selected.periode_name
    
    #matieres = Matieres.objects.filter(notes__trimestre=trimestre_selected, notes__eleve__classe=classe).distinct()

    # Calcul du nombre d'élèves ayant la moyenne par matière et par sexe
    data = {'matieres': [], 'moyenne_par_matiere': [], 'nombre_de_9_par_matiere': [], 'nombre_de_8_par_matiere': [], 'nombre_de_7_par_matiere': [], 'nombre_de_6_par_matiere': [], 'moyenne_par_sexe': {'M': [], 'F': []}, 'nombre_de_9_par_sexe': {'M': [], 'F': []}, 'nombre_de_8_par_sexe': {'M': [], 'F': []}, 'nombre_de_7_par_sexe': {'M': [], 'F': []}, 'nombre_de_6_par_sexe': {'M': [], 'F': []}, 'pourcentage_moyenne_par_matiere': [], 'pourcentage_notes_8_par_matiere': [], 'pourcentage_notes_7_par_matiere': [], 'pourcentage_notes_6_par_matiere': [], 'pourcentage_moyenne_par_sexe': {'M': [], 'F': []}}

    content = []

    # Ajouter le titre du document
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    content.append(Paragraph(f"Statistiques pour la classe {classe.classe_name}", title_style))


    for matiere in matieres:
        eleves_matiere = Note.objects.filter(matiere=matiere, trimestre=trimestre_selected)
        
        # Filter out the Notes with moyenne_matiere as None
        eleves_matiere = [note for note in eleves_matiere if note.moyenne_matiere is not None]
        
        eleves_moyenne = [eleve for eleve in eleves_matiere if eleve.moyenne_matiere >= 10]
        
        data['matieres'].append(matiere.matiere_name)
        data['moyenne_par_matiere'].append(len(eleves_moyenne))
        
        total_eleves = len(eleves_matiere)
        pourcentage_moyenne = (len(eleves_moyenne) / total_eleves) * 100 if total_eleves > 0 else 0
        
        
        data['pourcentage_moyenne_par_matiere'].append(pourcentage_moyenne)
        

        eleves_moyenne_par_sexe = {'M': 0, 'F': 0}
        for eleve in eleves_moyenne:
            eleves_moyenne_par_sexe[eleve.eleve.gender] += 1

        data['moyenne_par_sexe']['M'].append(eleves_moyenne_par_sexe['M'])
        data['moyenne_par_sexe']['F'].append(eleves_moyenne_par_sexe['F'])

        pourcentage_moyenne_homme = (eleves_moyenne_par_sexe['M'] / total_eleves) * 100 if total_eleves > 0 else 0
        pourcentage_moyenne_femme = (eleves_moyenne_par_sexe['F'] / total_eleves) * 100 if total_eleves > 0 else 0

        data['pourcentage_moyenne_par_sexe']['M'].append(pourcentage_moyenne_homme)
        data['pourcentage_moyenne_par_sexe']['F'].append(pourcentage_moyenne_femme)

        

    # ... (copiez le reste de votre logique de récupération des données)

    # template = get_template("Gestbull/show-classe-statistiques.html")
    # context = {'classe': classe, 'eleves': eleves, 'matieres': matieres, 'trimestre': trimestre_selected, 'chart_data': data}

    # html = template.render(context)
    buffer = BytesIO()

    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Ajouter les graphiques dans le document PDF
    moyenne_par_matiere_chart = create_chart(data['matieres'], data['moyenne_par_matiere'], "Nombre d'élèves avec moyenne par matière")
    moyenne_par_sexe_chart = create_dual_chart(data['matieres'], data['moyenne_par_sexe']['M'], data['moyenne_par_sexe']['F'], "Nombre d'élèves avec moyenne par matière et par sexe")

    content.append(Image(moyenne_par_matiere_chart, width=500, height=400))
    content.append(Image(moyenne_par_sexe_chart, width=500, height=400))
    
    
    
    # Construire le document PDF
    doc.build(content)

    # Récupérer le PDF généré
    pdf = buffer.getvalue()
    buffer.close()

    # Renvoyer la réponse HTTP avec le PDF en pièce jointe
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="statistiques_{classe.classe_name}.pdf"'
    return response

def create_chart(labels, values, title):
    positions = range(len(labels))
    plt.bar( labels, values, color=(0.29, 0.75, 0.75, 0.2), edgecolor=(0.29, 0.75, 0.75, 1))
    for position, value in zip(positions, values):
        plt.text(position, value, str(value), ha='center', va='bottom')
        
    plt.title(title)
    plt.xlabel('Matières')
    plt.ylabel("Nombre d'élèves")
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close()
    return chart_buffer

def create_dual_chart(labels, values_m, values_f, title):
    bar_width = 0.35
    positions_m = range(len(labels))
    positions_f = [pos + bar_width for pos in positions_m]

    plt.bar(positions_m, values_m, width=bar_width, color=(1, 0.39, 0.52, 0.7), edgecolor=(0.25, 0.39, 0.52, 0.25), label='Masculin')
    plt.bar(positions_f, values_f, width=bar_width, color=(0.21, 0.64, 0.92, 0.7), edgecolor=(0.21, 0.64, 0.92, 1), label='Féminin')

    for pos_m, value_m, pos_f, value_f in zip(positions_m, values_m, positions_f, values_f):
        plt.text(pos_m, value_m, str(value_m), ha='center', va='bottom')
        plt.text(pos_f, value_f, str(value_f), ha='center', va='bottom')

    plt.title(title)
    plt.xlabel('Matières')
    plt.ylabel("Nombre d'élèves")
    plt.xticks(positions_m, labels)
    plt.legend()
    plt.tight_layout()
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close()
    return chart_buffer

