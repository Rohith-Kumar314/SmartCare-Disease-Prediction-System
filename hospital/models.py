from django.db import models
from django.contrib.auth.models import User



# departments=[('Cardiologist','Cardiologist'),
# ('Dermatologists','Dermatologists'),
# ('Emergency Medicine Specialists','Emergency Medicine Specialists'),
# ('Allergists/Immunologists','Allergists/Immunologists'),
# ('Anesthesiologists','Anesthesiologists'),
# ('Colon and Rectal Surgeons','Colon and Rectal Surgeons')
# ]

# class Doctor(models.Model):
#     user=models.OneToOneField(User,on_delete=models.CASCADE)
#     profile_pic= models.ImageField(upload_to='profile_pic/DoctorProfilePic/',null=True,blank=True)
#     address = models.CharField(max_length=40)
#     mobile = models.CharField(max_length=20,null=True)
#     department= models.CharField(max_length=50,choices=departments,default='Cardiologist')
#     status=models.BooleanField(default=False)
#     @property
#     def get_name(self):
#         return self.user.first_name+" "+self.user.last_name
#     @property
#     def get_id(self):
#         return self.user.id
#     def __str__(self):
#         return "{} ({})".format(self.user.first_name,self.department)

departments = [
    ('Cardiologist', 'Cardiologist'),
    ('Neurologist', 'Neurologist'),
    ('Pulmonologist', 'Pulmonologist'),
    ('Gastroenterologist', 'Gastroenterologist'),
    ('Hepatologist', 'Hepatologist'),
    ('Endocrinologist', 'Endocrinologist'),
    ('Nephrologist', 'Nephrologist'),
    ('General Doctor', 'General Doctor'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons')
]

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=50, choices=departments, default='Cardiologist')
    status = models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return "{} ({})".format(self.user.first_name, self.department)


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/PatientProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    symptoms = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=50, null=True)
    admitDate = models.DateField(null=True, blank=True)
    status = models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        mobile = f" ({self.mobile})" if self.mobile else ""
        return f"{self.user.first_name} {self.user.last_name}{mobile}"

class Appointment(models.Model):
    patientId=models.PositiveIntegerField(null=True)
    doctorId=models.PositiveIntegerField(null=True)
    patientName=models.CharField(max_length=40,null=True)
    doctorName=models.CharField(max_length=40,null=True)
    appointmentDate=models.DateField(auto_now=True)
    description=models.TextField(max_length=500)
    status=models.BooleanField(default=False)
    symptoms = models.CharField(max_length=255, null=True, blank=True)  # New field for extracted symptoms


class PatientDischargeDetails(models.Model):
    patientId=models.PositiveIntegerField(null=True)
    patientName=models.CharField(max_length=40)
    assignedDoctorName=models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=True)
    symptoms = models.CharField(max_length=100,null=True)

    admitDate=models.DateField(null=False)
    releaseDate=models.DateField(null=False)
    daySpent=models.PositiveIntegerField(null=False)

    roomCharge=models.PositiveIntegerField(null=False)
    medicineCost=models.PositiveIntegerField(null=False)
    doctorFee=models.PositiveIntegerField(null=False)
    OtherCharge=models.PositiveIntegerField(null=False)
    total=models.PositiveIntegerField(null=False)


# Adding new Models for the project to set availability and apply for leave for the doctor
from django.db import models
from django.contrib.auth.models import User

# (Assuming you already have a Doctor model defined elsewhere)

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.get_name} - {self.date} ({self.start_time} to {self.end_time})"

class DoctorLeave(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    leave_start = models.DateField()
    leave_end = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default="Pending")  # Options: Pending, Approved, Rejected

    def __str__(self):
        return f"{self.doctor.get_name} Leave: {self.leave_start} to {self.leave_end}"


class Prescription(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)  # Linking to Patient Model
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)  # Linking to Doctor Model
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)  # Linking to Appointment
    medicines = models.TextField()  # Stores list of medicines
    instructions = models.TextField()  # General instructions
    precautions = models.TextField()  # Any precautions the patient should follow
    prescribed_date = models.DateTimeField(auto_now_add=True)  # Auto timestamp when prescribed

    def __str__(self):
        return f"Prescription for {self.patient.user.get_full_name()} by Dr. {self.doctor.user.get_full_name()}"

class PatientPrediction(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)  # Links to Patient
    symptoms = models.TextField()  # Stores symptoms as a text field
    predicted_disease = models.CharField(max_length=255)  # Stores the predicted disease
    prediction_date = models.DateTimeField(auto_now_add=True)  # Timestamp when prediction is made

    def __str__(self):
        return f"Prediction for {self.patient.user.get_full_name()}: {self.predicted_disease}"
