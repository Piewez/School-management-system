from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg, Sum, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
import qrcode
from io import BytesIO
from django.core.files import File
from decimal import Decimal

# Create your models here.
class SessionYearModel(models.Model):
    id=models.AutoField(primary_key=True)
    session_start_year=models.DateField()
    session_end_year=models.DateField()
    nom = models.CharField(max_length=100)
    is_complete = models.BooleanField(default=False)  # Champ pour indiquer la fin de l'année scolaire
    
    objects=models.Manager()

    def __str__(self):
        return self.nom
    
    @classmethod
    def get_current_session(cls):
        return cls.objects.filter(is_complete=False).first()
    

    # Méthode pour récupérer les périodes associées à cette année scolaire
    def get_periodes(self):
        return self.periodes.all()

class Periode(models.Model):
    periode_name = models.CharField(max_length=100, choices=[
        ('1er Trimestre', '1er Trimestre'), 
        ('2ème Trimestre', '2ème Trimestre'), 
        ('3ème Trimestre', '3ème Trimestre'), 
        ('1er Semestre', '1er Semestre'),
        ('2ème Semestre', '2ème Semestre'),
        ])
    annee_scolaire = models.ForeignKey('SessionYearModel', on_delete=models.CASCADE, related_name='periodes')

    # Ajoutez d'autres champs nécessaires pour représenter une période (dates, détails, etc.)
    
    
    def __str__(self):
        return self.periode_name

class CustomUser(AbstractUser):
    user_type_data=(
        (1,"HOD"),
        (2,"Professeur"),
        (3,"Student"), 
        (4,"Econome"), 
        (5,"Secretaire"), 
        (6,"Surveillant"), 
        (7,"Biblioteque"),
        (8,"Cantine"), 
        (9,"Medecine"),
        )
    user_type=models.CharField(default=1,choices=user_type_data,max_length=20)

class AdminHOD(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class Professeurs(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects=models.Manager()
    
    def nombre_eleves_enseignes(self):
        # Utilisez l'agrégation pour obtenir le nombre total d'élèves
        return self.matieres_enseignees().annotate(total_students=Count('classe_id__students')).aggregate(Sum('total_students'))['total_students__sum'] or 0

    def matieres_enseignees(self):
        return self.matieres.all()

class Economes(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects=models.Manager()
    
    def nombre_eleves_enseignes(self):
        # Utilisez l'agrégation pour obtenir le nombre total d'élèves
        return self.matieres_enseignees().annotate(total_students=Count('classe_id__students')).aggregate(Sum('total_students'))['total_students__sum'] or 0

    def matieres_enseignees(self):
        return self.matieres.all()

class Secretaire(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects=models.Manager()
    
    def nombre_eleves_enseignes(self):
        # Utilisez l'agrégation pour obtenir le nombre total d'élèves
        return self.matieres_enseignees().annotate(total_students=Count('classe_id__students')).aggregate(Sum('total_students'))['total_students__sum'] or 0

    def matieres_enseignees(self):
        return self.matieres.all()

class Bibliotheque(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects=models.Manager()
    
    def nombre_eleves_enseignes(self):
        # Utilisez l'agrégation pour obtenir le nombre total d'élèves
        return self.matieres_enseignees().annotate(total_students=Count('classe_id__students')).aggregate(Sum('total_students'))['total_students__sum'] or 0

    def matieres_enseignees(self):
        return self.matieres.all()

class Surveillant(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects=models.Manager()
    
    def nombre_eleves_enseignes(self):
        # Utilisez l'agrégation pour obtenir le nombre total d'élèves
        return self.matieres_enseignees().annotate(total_students=Count('classe_id__students')).aggregate(Sum('total_students'))['total_students__sum'] or 0

    def matieres_enseignees(self):
        return self.matieres.all()

class Cycles(models.Model):
    cycle_name = models.CharField(max_length=50)

class Classes(models.Model):
    id=models.AutoField(primary_key=True)
    classe_name=models.CharField(max_length=255)
    titulaire = models.ForeignKey('Professeurs', on_delete=models.SET_NULL, null=True, related_name='classes')
    #cycle = models.ForeignKey('Cycles', on_delete=models.SET_NULL, null=True, related_name='classes')
    
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class CategorieMatiere(models.Model):
    nom = models.CharField(max_length=100)
    
class Matieres(models.Model):
    id=models.AutoField(primary_key=True)
    matiere_name=models.CharField(max_length=255)
    classe_id=models.ForeignKey(Classes,on_delete=models.CASCADE,default=1)
    professeur_id=models.ForeignKey('Professeurs', on_delete=models.SET_NULL, null=True, related_name='matieres',default=1)
    coefficient = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    categorie = models.ForeignKey('CategorieMatiere', on_delete=models.SET_NULL, null=True, related_name='matieres')
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class Students(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    numero_matricule = models.CharField(max_length=50)
    gender=models.CharField(max_length=255)
    statut = models.CharField(max_length=50, null=True, blank=True)
    profile_pic=models.FileField()
    address=models.TextField()
    date_naissance = models.DateField()
    contact_parent = models.CharField(max_length=100, null=True, blank=True)
    
    # Champ pour l'aptitude au sport
    aptitude_sport = models.CharField(max_length=10)
    
    classe_id=models.ForeignKey('Classes', on_delete=models.CASCADE, related_name='students', default=1)
    
    annee_scolaire = models.ForeignKey('SessionYearModel', on_delete=models.CASCADE, related_name='students')
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    objects = models.Manager()
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.numero_matricule)
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer)
            file_name = f'qr_{self.numero_matricule}.png'
            self.qr_code.save(file_name, File(buffer), save=False)
        super().save(*args, **kwargs)
    
    def calculer_moyenne_par_periode(self, periode):
        notes = Note.objects.filter(eleve=self, trimestre=periode)
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
                eleve=self, 
                periode=periode, 
                defaults={'moyenne': moyenne}
            )
            return moyenne_obj


    def attribuer_rang_par_periode(self, periode):
        moyennes = Moyenne.objects.filter(periode=periode).order_by('-moyenne')
        for index, moyenne in enumerate(moyennes):
            moyenne.rang = index + 1
            moyenne.save()
            
    
    def calculer_moyenne_annuelle(self, annee_scolaire):
        periodes = Periode.objects.filter(annee_scolaire=annee_scolaire)
        moyennes = Moyenne.objects.filter(eleve=self, periode__in=periodes)
        
        if moyennes.exists():
            total_moyennes = sum(moyenne.moyenne for moyenne in moyennes if moyenne.moyenne is not None)
            moyenne_annuelle = total_moyennes / moyennes.count()
            
            # Créer ou mettre à jour la moyenne annuelle
            moyenne_annuelle_obj, created = MoyenneAnnuelle.objects.update_or_create(
                eleve=self, 
                annee_scolaire=annee_scolaire, 
                defaults={'moyenne': moyenne_annuelle}
            )
            return moyenne_annuelle_obj
        
    def attribuer_rang_annuel(self, annee_scolaire):
        moyennes_annuelles = MoyenneAnnuelle.objects.filter(annee_scolaire=annee_scolaire).order_by('-moyenne')
        for index, moyenne_annuelle in enumerate(moyennes_annuelles):
            moyenne_annuelle.rang = index + 1
            moyenne_annuelle.save()

class Attendance(models.Model):
    id=models.AutoField(primary_key=True)
    matiere_id=models.ForeignKey(Matieres,on_delete=models.DO_NOTHING)
    attendance_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    session_year_id=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class AttendanceReport(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Students,on_delete=models.DO_NOTHING)
    attendance_id=models.ForeignKey(Attendance,on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class LeaveReportStudent(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Students,on_delete=models.CASCADE)
    leave_date=models.CharField(max_length=255)
    leave_message=models.TextField()
    leave_status=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class LeaveReportProfesseur(models.Model):
    id = models.AutoField(primary_key=True)
    professeur_id = models.ForeignKey(Professeurs, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class FeedBackProfesseurs(models.Model):
    id = models.AutoField(primary_key=True)
    professeur_id = models.ForeignKey(Professeurs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class NotificationProfesseurs(models.Model):
    id = models.AutoField(primary_key=True)
    professeur_id = models.ForeignKey(Professeurs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class StudentResult(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Students,on_delete=models.CASCADE)
    matiere_id=models.ForeignKey(Matieres,on_delete=models.CASCADE)
    matiere_exam_marks=models.FloatField(default=0)
    matiere_assignment_marks=models.FloatField(default=0)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now_add=True)
    objects=models.Manager()

class OnlineClassRoom(models.Model):
    id=models.AutoField(primary_key=True)
    room_name=models.CharField(max_length=255)
    room_pwd=models.CharField(max_length=255)
    matiere=models.ForeignKey(Matieres,on_delete=models.CASCADE)
    session_years=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    started_by=models.ForeignKey(Professeurs,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    created_on=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()


class MoyenneCategorie(models.Model):
    eleve = models.ForeignKey('Students', on_delete=models.CASCADE, related_name='moyennes_categorie')
    categorie = models.ForeignKey('CategorieMatiere', on_delete=models.CASCADE, related_name='moyennes')
    periode = models.ForeignKey('Periode', on_delete=models.CASCADE, related_name='moyennes_categorie')
    moyenne = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rang = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('eleve', 'categorie', 'periode')

    def __str__(self):
        return f"Moyenne de {self.eleve} pour {self.categorie} en {self.periode}: {self.moyenne}"


class Note(models.Model):
    eleve = models.ForeignKey('Students', on_delete=models.CASCADE, related_name='notes')
    matiere = models.ForeignKey('Matieres', on_delete=models.CASCADE, related_name='notes')
    coefficient = models.DecimalField(max_digits=5, decimal_places=2)
    trimestre = models.ForeignKey('Periode', on_delete=models.CASCADE, related_name='notes')
    evaluation_classe = models.DecimalField(max_digits=5, decimal_places=2, validators=[MaxValueValidator(20)])
    devoir = models.DecimalField(max_digits=5, decimal_places=2, validators=[MaxValueValidator(20)])
    composition = models.DecimalField(max_digits=5, decimal_places=2, validators=[MaxValueValidator(20)])
    moyenne_matiere = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rang_matiere = models.IntegerField(null=True, blank=True)  # Nouveau champ pour le rang par matière
    numero_matiere = models.IntegerField(null=True, blank=True, default=1)  # Nouveau champ pour le rang par matière
    moyenne_categorie = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def clean(self):
        if self.evaluation_classe > 20 or self.devoir > 20 or self.composition > 20:
            raise ValidationError("La note ne peut pas dépasser 20.")
        elif self.evaluation_classe < 20 or self.devoir < 20 or self.composition < 20:
            raise ValidationError("La note ne peut pas être négative.")
        
    def calculer_moyenne_categorie(self):
        categorie = self.matiere.categorie

        # Récupérer toutes les notes de l'élève pour les matières de la même catégorie
        notes_categorie = Note.objects.filter(
            eleve=self.eleve,
            matiere__categorie=categorie,
            trimestre=self.trimestre
        )

        # Calcul de la moyenne pondérée pour la catégorie
        total_pondered = sum(note.moyenne_matiere * note.coefficient for note in notes_categorie)
        total_coefficients = sum(note.coefficient for note in notes_categorie)

        if total_coefficients > 0:
            self.moyenne_categorie = total_pondered / total_coefficients
        else:
            self.moyenne_categorie = None

        self.save()
        return self.moyenne_categorie


    def calculer_moyenne_matiere(self):
        # Conversion des valeurs en Decimal pour assurer des calculs corrects
        evaluation_classe = Decimal(self.evaluation_classe)
        devoir = Decimal(self.devoir)
        composition = Decimal(self.composition)
        
        # Calcul de la moyenne
        moyenne_note = (((evaluation_classe + devoir) / 2) + composition) / 2
        
        # Affectation de la moyenne à l'attribut moyenne_matiere
        self.moyenne_matiere = moyenne_note
        self.save()
        return moyenne_note

    def attribuer_rang_matiere(self):
        # Calculer la moyenne si ce n'est pas déjà fait
        self.calculer_moyenne_matiere()
        
        # Récupérer toutes les notes pour la matière et le trimestre actuels
        notes_matiere_trimestre = Note.objects.filter(
            matiere=self.matiere, 
            trimestre=self.trimestre
        ).order_by('-moyenne_matiere')
        
        for index, note in enumerate(notes_matiere_trimestre):
            # Créer ou mettre à jour le rang pour chaque élève
            rang_matiere, created = RangMatiere.objects.update_or_create(
                eleve=note.eleve,
                matiere=self.matiere,
                periode=self.trimestre,
                defaults={
                    'rang': index + 1,
                    'moyenne_matiere': note.moyenne_matiere,
                }
            )

        
        # Mettre à jour le champ rang_matiere pour chaque note dans l'ordre décroissant de la moyenne de la matière
        for index, note in enumerate(notes_matiere_trimestre):
            rang_matiere = note.mettre_a_jour_rang_matiere(index + 1)
            self.rang_matiere = rang_matiere
            self.save()
            
    def mettre_a_jour_rang_matiere(self, nouvelle_rang):
        self.rang_matiere = nouvelle_rang
        self.save()

        

    def __str__(self):
        eleve_nom = self.eleve.admin.first_name if self.eleve and self.eleve.admin.first_name else "Sans nom d'élève"
        matiere_nom = self.matiere.matiere_name if self.matiere and self.matiere.matiere_name else "Sans nom de matière"
        trimestre_nom = self.trimestre.nom if self.trimestre and self.trimestre.nom else "Sans nom de trimestre"

        return f"{eleve_nom} - {matiere_nom} - {trimestre_nom}"

    class Meta:
        unique_together = ('eleve', 'matiere', 'trimestre')


class ExamenBlanc(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)  # BAC1, BAC2, etc.
    classes_concernees = models.ManyToManyField(Classes, related_name='examens_blancs')
    annee_scolaire = models.ForeignKey('SessionYearModel', on_delete=models.CASCADE, related_name='examens_blancs')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager()
    
    def assigner_numero_table(self):
        # Récupérer les élèves des classes concernées
        students = Students.objects.filter(classe_id__in=self.classes_concernees.all()).order_by('admin__first_name', 'admin__last_name')
        
        # Assigner un numéro de table
        for i, student in enumerate(students, start=2000):
            NumeroTableExamen.objects.create(
                examen_blanc=self,
                student=student,
                numero_table=i
            )

class NumeroTableExamen(models.Model):
    examen_blanc = models.ForeignKey(ExamenBlanc, on_delete=models.CASCADE, related_name='numero_tables')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='examens_blancs')
    numero_table = models.IntegerField()
    moyenne = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rang = models.IntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ('examen_blanc', 'numero_table')
        ordering = ['numero_table']  # Par ordre croissant des numéros de table


class ExamenNote(models.Model):
    examen = models.ForeignKey('ExamenBlanc', on_delete=models.CASCADE, related_name='examen_notes')
    numero_table_eleve = models.ForeignKey('NumeroTableExamen', on_delete=models.CASCADE, related_name='examen_notes')
    matiere = models.ForeignKey('Matieres', on_delete=models.CASCADE, related_name='examen_notes')
    coefficient = models.DecimalField(max_digits=5, decimal_places=2)
    note = models.DecimalField(max_digits=5, decimal_places=2, validators=[MaxValueValidator(20)])
    rang_matiere = models.IntegerField(null=True, blank=True)  # Nouveau champ pour le rang par matière
    numero_matiere = models.IntegerField(null=True, blank=True, default=1)  # Nouveau champ pour le rang par matière
    moyenne_categorie = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
    
    def attribuer_rang_matiere(self):
        # Calculer la moyenne si ce n'est pas déjà fait
        self.note
        
        # Récupérer toutes les notes pour la matière et le trimestre actuels
        notes_matiere_examen = ExamenNote.objects.filter(
            matiere=self.matiere, 
            examen=self.examen
        ).order_by('-note')

        
        # Mettre à jour le champ rang_matiere pour chaque note dans l'ordre décroissant de la moyenne de la matière
        for index, note in enumerate(notes_matiere_examen):
            rang_matiere = note.mettre_a_jour_rang_matiere(index + 1)
            self.rang_matiere = rang_matiere
            self.save()
            
    def mettre_a_jour_rang_matiere(self, nouvelle_rang):
        self.rang_matiere = nouvelle_rang
        self.save()


class MoyenneExamen(models.Model):
    examen = models.ForeignKey('ExamenBlanc', on_delete=models.CASCADE, related_name='moyenne_examen')
    numero_table_eleve = models.ForeignKey('NumeroTableExamen', on_delete=models.CASCADE, related_name='moyenne_examen')
    moyenne = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rang = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Moyenne de {self.numero_table_eleve} pour {self.examen}: {self.moyenne}"

class Moyenne(models.Model):
    eleve = models.ForeignKey('Students', on_delete=models.CASCADE, related_name='moyennes')
    periode = models.ForeignKey('Periode', on_delete=models.CASCADE, related_name='moyennes')
    moyenne = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rang = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Moyenne de {self.eleve} pour {self.periode}: {self.moyenne}"


class MoyenneAnnuelle(models.Model):
    eleve = models.ForeignKey('Students', on_delete=models.CASCADE, related_name='moyennes_annuelles')
    annee_scolaire = models.ForeignKey('SessionYearModel', on_delete=models.CASCADE, related_name='moyennes_annuelles')
    moyenne = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rang = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Moyenne annuelle de {self.eleve} pour {self.annee_scolaire}: {self.moyenne}"


class RangMatiere(models.Model):
    eleve = models.ForeignKey('Students', on_delete=models.CASCADE, related_name='rangs_matiere')
    matiere = models.ForeignKey('Matieres', on_delete=models.CASCADE, related_name='rangs_matiere')
    periode = models.ForeignKey('Periode', on_delete=models.CASCADE, related_name='rangs_matiere')
    rang = models.IntegerField(null=True, blank=True)
    moyenne_matiere = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('eleve', 'matiere', 'periode')

    def __str__(self):
        return f"Rang de {self.eleve} en {self.matiere} pour {self.periode}: {self.rang}"
    
    


class Bulletin(models.Model):
    eleve = models.ForeignKey('Students', on_delete=models.CASCADE, related_name='bulletins')
    annee_scolaire = models.ForeignKey('SessionYearModel', on_delete=models.CASCADE, related_name='bulletins')
    periode = models.ForeignKey('Periode', on_delete=models.CASCADE, related_name='bulletins', null=True, blank=True)
    moyenne_annuelle = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rang_annuel = models.IntegerField(null=True, blank=True)
    moyennes_periodes = models.JSONField(default=dict)  # Pour stocker les moyennes par période
    rangs_periodes = models.JSONField(default=dict)  # Pour stocker les rangs par période
    commentaire = models.TextField(null=True, blank=True)  # Optionnel: un champ pour des commentaires

    def __str__(self):
        periode_info = f" pour {self.periode}" if self.periode else ""
        return f"Bulletin de {self.eleve} pour {self.annee_scolaire}{periode_info}"
        
class PaymentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='payments')
    category = models.ForeignKey(PaymentCategory, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.admin.username} - {self.category.name} - {self.amount} CFA"

    class Meta:
        unique_together = ('student', 'category', 'payment_date')



class Comportement(models.Model):
    ASPECT_CHOICES = [
        ('retard', 'Retard'),
        ('absence', 'Absence'),
        ('participation', 'Participation en classe'),
        ('qualite_travail', 'Qualité du travail'),
        ('engagement', 'Engagement'),
        ('proprete', 'Propreté du matériel'),
        ('respect_regles', 'Respect des règles'),
    ]
    aspect = models.CharField(max_length=20, choices=ASPECT_CHOICES)
    points = models.PositiveIntegerField()
    student = models.ForeignKey('Students', on_delete=models.CASCADE, related_name='comportements')
    periode = models.ForeignKey('Periode', on_delete=models.CASCADE, related_name='comportements')
    date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.pk:  # On ne définit les points que lors de la création
            self.points = self.get_points_for_aspect(self.aspect)
        super().save(*args, **kwargs)

    def get_points_for_aspect(self, aspect):
        points_mapping = {
            'retard': 1,
            'absence': 2,
            'participation': 1,
            'qualite_travail': 3,
            'engagement': 2,
            'proprete': 1,
            'respect_regles': 1,
        }
        return points_mapping.get(aspect, 0)  # Retourne 0 si l'aspect n'est pas défini







@receiver(post_save,sender=CustomUser)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        if instance.user_type==1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type==2:
            Professeurs.objects.create(admin=instance,address="")
        if instance.user_type==3:
            default_classe = Classes.objects.first()
        if default_classe:
            Students.objects.create(admin=instance, classe_id=default_classe, annee_scolaire=SessionYearModel.get_current_session(),address="",profile_pic="",gender="",numero_matricule="",statut="",date_naissance="2000-12-31",contact_parent="",aptitude_sport="")
        else:
            # Gérer le cas où aucune classe n'existe (afficher un message d'erreur ou créer une classe par défaut)
            raise ValueError("No classes available to assign to the student.")

        if instance.user_type==4:
            Economes.objects.create(admin=instance,address="")

@receiver(post_save,sender=CustomUser)
def save_user_profile(sender,instance,**kwargs):
    if instance.user_type==1:
        instance.adminhod.save()
    if instance.user_type==2:
        instance.professeurs.save()
    if instance.user_type==3:
        instance.students.save()
    if instance.user_type==4:
        instance.economes.save()
