from django import forms
from django.forms import ChoiceField

from student_management_app.models import Classes, SessionYearModel, Matieres, Students, SessionYearModel

class ChoiceNoValidation(ChoiceField):
    def validate(self, value):
        pass

class DateInput(forms.DateInput):
    input_type = "date"

class AddStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "off"}))
    # Supprimer le champ password si vous souhaitez définir un mot de passe par défaut
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class": "form-control"}), required=False)
    first_name = forms.CharField(label="NOM", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Prénoms", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(label="Addresse", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    numero_matricule = forms.CharField(label="N° Matricule", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    statut = forms.CharField(label="Statut", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    contact_parent = forms.CharField(label="Contact Parent", max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    date_naissance = forms.DateField(label="Date de Naissance", widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}))
    aptitude_sport = forms.ChoiceField(label="Aptitude Sport", choices=(('Apte', 'Apte'), ('Inapte', 'Inapte')), widget=forms.Select(attrs={"class": "form-control"}))

    gender_choice = (("M", "M"), ("F", "F"))
    sex = forms.ChoiceField(label="Sexe", choices=gender_choice, widget=forms.Select(attrs={"class": "form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", max_length=50, widget=forms.FileInput(attrs={"class": "form-control"}), required=False)

    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        classes = Classes.objects.all()
        classe_list = [(classe.id, classe.classe_name) for classe in classes]
        self.fields['classe'] = forms.ChoiceField(label="Classe", choices=classe_list, widget=forms.Select(attrs={"class": "form-control"}))
        
        current_session = SessionYearModel.get_current_session()
        if current_session:
            self.fields['annee_scolaire'] = forms.ChoiceField(
                label="Année Scolaire",
                choices=[(current_session.id, current_session.nom)],
                widget=forms.Select(attrs={"class": "form-control"})
            )
        else:
            self.fields['annee_scolaire'] = forms.ChoiceField(
                label="Année Scolaire",
                choices=[],
                widget=forms.Select(attrs={"class": "form-control"})
            )


# class AddStudentForm(forms.Form):
#     email=forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control","autocomplete":"off"}))
#     password=forms.CharField(label="Password",max_length=50,widget=forms.PasswordInput(attrs={"class":"form-control"}))
#     first_name=forms.CharField(label="NOM",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     last_name=forms.CharField(label="Prénoms",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     username=forms.CharField(label="Username",max_length=50,widget=forms.TextInput(attrs={"class":"form-control","autocomplete":"off"}))
#     address=forms.CharField(label="Addresse",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     numero_matricule=forms.CharField(label="N° Matricule",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     statut=forms.CharField(label="Statut",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     address=forms.CharField(label="Address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     contact_parent = forms.CharField(label="Contact Parent", max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
#     #sex = forms.ChoiceField(label="Sex", choices=(("M", "M"), ("F", "F")), widget=forms.Select(attrs={"class": "form-control"}))
#     date_naissance = forms.DateField(label="Date de Naissance", widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}))
#     aptitude_sport = forms.ChoiceField(label="Aptitude Sport", choices=(('Apte', 'Apte'), ('Inapte', 'Inapte')), widget=forms.Select(attrs={"class": "form-control"}))



#     gender_choice=(
#         ("M","M"),
#         ("F","F")
#     )

#     sex=forms.ChoiceField(label="Sexe",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
#     profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}))
    
#     def __init__(self, *args, **kwargs):
#         super(AddStudentForm, self).__init__(*args, **kwargs)
#         classes = Classes.objects.all()
#         classe_list = [(classe.id, classe.classe_name) for classe in classes]
#         self.fields['classe'] = forms.ChoiceField(label="Classe", choices=classe_list, widget=forms.Select(attrs={"class": "form-control"}))
        
#         current_session = SessionYearModel.get_current_session()
#         if current_session:
#             self.fields['annee_scolaire'] = forms.ChoiceField(
#                 label="Année Scolaire",
#                 choices=[(current_session.id, current_session.nom)],
#                 widget=forms.Select(attrs={"class": "form-control"})
#             )
#         else:
#             # Gérer le cas où il n'y a pas d'année scolaire en cours
#             self.fields['annee_scolaire'] = forms.ChoiceField(
#                 label="Année Scolaire",
#                 choices=[],
#                 widget=forms.Select(attrs={"class": "form-control"})
#             )

class EditStudentForm(forms.Form):
    email=forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control","autocomplete":"off"}))
    first_name=forms.CharField(label=" NOM",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name=forms.CharField(label="Prénoms",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    username=forms.CharField(label="Username",max_length=50,widget=forms.TextInput(attrs={"class":"form-control","autocomplete":"off"}))
    address=forms.CharField(label="Address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    numero_matricule=forms.CharField(label="N° Matricule",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    statut=forms.CharField(label="Statut",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    address=forms.CharField(label="Addresse",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    contact_parent = forms.CharField(label="Contact Parent", max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    #sex = forms.ChoiceField(label="Sex", choices=(("M", "M"), ("F", "F")), widget=forms.Select(attrs={"class": "form-control"}))
    date_naissance = forms.DateField(label="Date de Naissance", widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}))
    aptitude_sport = forms.ChoiceField(label="Aptitude Sport", choices=(('Apte', 'Apte'), ('Inapte', 'Inapte')), widget=forms.Select(attrs={"class": "form-control"}))



    gender_choice=(
        ("M","M"),
        ("F","F")
    )

    sex=forms.ChoiceField(label="Sexe",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}), required=False)
    
    def __init__(self, *args, **kwargs):
        super(EditStudentForm, self).__init__(*args, **kwargs)
        classes = Classes.objects.all()
        classe_list = [(classe.id, classe.classe_name) for classe in classes]
        self.fields['classe'] = forms.ChoiceField(label="Classe", choices=classe_list, widget=forms.Select(attrs={"class": "form-control"}))
        
        current_session = SessionYearModel.get_current_session()
        if current_session:
            self.fields['annee_scolaire'] = forms.ChoiceField(
                label="Année Scolaire",
                choices=[(current_session.id, current_session.nom)],
                widget=forms.Select(attrs={"class": "form-control"})
            )
        else:
            # Gérer le cas où il n'y a pas d'année scolaire en cours
            self.fields['annee_scolaire'] = forms.ChoiceField(
                label="Année Scolaire",
                choices=[],
                widget=forms.Select(attrs={"class": "form-control"})
            )

class EditResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.professeur_id=kwargs.pop("professeur_id")
        super(EditResultForm,self).__init__(*args,**kwargs)
        matiere_list=[]
        try:
            matieres=Matieres.objects.filter(professeur_id=self.professeur_id)
            for matiere in matieres:
                matiere_single=(matiere.id,matiere.matiere_name)
                matiere_list.append(matiere_single)
        except:
            matiere_list=[]
        self.fields['matiere_id'].choices=matiere_list

    session_list=[]
    try:
        sessions=SessionYearModel.objects.all()
        for session in sessions:
            session_single=(session.id,str(session.session_start_year)+" TO "+str(session.session_end_year))
            session_list.append(session_single)
    except:
        session_list=[]

    matiere_id=forms.ChoiceField(label="Matiere",widget=forms.Select(attrs={"class":"form-control"}))
    session_ids=forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
    student_ids=ChoiceNoValidation(label="Student",widget=forms.Select(attrs={"class":"form-control"}))
    assignment_marks=forms.CharField(label="Assignment Marks",widget=forms.TextInput(attrs={"class":"form-control"}))
    exam_marks=forms.CharField(label="Exam Marks",widget=forms.TextInput(attrs={"class":"form-control"}))


class AddPeriodeForm(forms.Form):
    periode_choice = (        
        ('1er Trimestre', '1er Trimestre'), 
        ('2ème Trimestre', '2ème Trimestre'), 
        ('3ème Trimestre', '3ème Trimestre'), 
        ('1er Semestre', '1er Semestre'),
        ('2ème Semestre', '2ème Semestre'),
        )
    nom = forms.ChoiceField(label="Nom", choices=periode_choice, widget=forms.Select(attrs={"class": "form-control"}))
    
    def __init__(self, *args, **kwargs):
        super(AddPeriodeForm, self).__init__(*args, **kwargs)
        annee_scolaires = SessionYearModel.objects.all()
        annee_scolaire_list = [(annee_scolaire.id, annee_scolaire.nom) for annee_scolaire in annee_scolaires]
        self.fields['annee_scolaire'] = forms.ChoiceField(label="Année Scolaire", choices=annee_scolaire_list, widget=forms.Select(attrs={"class": "form-control"}))



class EditPeriodeForm(forms.Form):
    periode_choice = (        
        ('1er Trimestre', '1er Trimestre'), 
        ('2ème Trimestre', '2ème Trimestre'), 
        ('3ème Trimestre', '3ème Trimestre'), 
        ('1er Semestre', '1er Semestre'),
        ('2ème Semestre', '2ème Semestre'),
        )
    nom = forms.ChoiceField(label="Nom", choices=periode_choice, widget=forms.Select(attrs={"class": "form-control"}))
    
    def __init__(self, *args, **kwargs):
        super(EditPeriodeForm, self).__init__(*args, **kwargs)
        annee_scolaires = SessionYearModel.objects.all()
        annee_scolaire_list = [(annee_scolaire.id, annee_scolaire.nom) for annee_scolaire in annee_scolaires]
        self.fields['annee_scolaire'] = forms.ChoiceField(label="Année Scolaire", choices=annee_scolaire_list, widget=forms.Select(attrs={"class": "form-control"}))


class AddExamenBlancForm(forms.Form):
    nom = forms.CharField(
        label="Nom de l'examen", 
        max_length=255, 
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    # Ajout de l'année scolaire (vous l'avez déjà bien commencé)
    def __init__(self, *args, **kwargs):
        super(AddExamenBlancForm, self).__init__(*args, **kwargs)
        
        # Récupérer les années scolaires
        annee_scolaires = SessionYearModel.objects.filter(is_complete=False)
        annee_scolaire_list = [(annee_scolaire.id, annee_scolaire.nom) for annee_scolaire in annee_scolaires]
        
        # Ajouter un champ pour l'année scolaire
        self.fields['annee_scolaire'] = forms.ChoiceField(
            label="Année Scolaire", 
            choices=annee_scolaire_list, 
            widget=forms.Select(attrs={"class": "form-control"})
        )
        
        # Récupérer les classes disponibles
        classes = Classes.objects.all()
        classes_list = [(classe.id, classe.classe_name) for classe in classes]
        
        # Ajouter un champ pour sélectionner les classes concernées
        self.fields['classes_concernees'] = forms.MultipleChoiceField(
            label="Classes Concernées", 
            choices=classes_list, 
            widget=forms.SelectMultiple(attrs={"class": "form-control"})
        )



class EditPeriodeForm(forms.Form):
    periode_choice = (        
        ('1er Trimestre', '1er Trimestre'), 
        ('2ème Trimestre', '2ème Trimestre'), 
        ('3ème Trimestre', '3ème Trimestre'), 
        ('1er Semestre', '1er Semestre'),
        ('2ème Semestre', '2ème Semestre'),
        )
    nom = forms.ChoiceField(label="Nom", choices=periode_choice, widget=forms.Select(attrs={"class": "form-control"}))
    
    def __init__(self, *args, **kwargs):
        super(EditPeriodeForm, self).__init__(*args, **kwargs)
        annee_scolaires = SessionYearModel.objects.all()
        annee_scolaire_list = [(annee_scolaire.id, annee_scolaire.nom) for annee_scolaire in annee_scolaires]
        self.fields['annee_scolaire'] = forms.ChoiceField(label="Année Scolaire", choices=annee_scolaire_list, widget=forms.Select(attrs={"class": "form-control"}))

