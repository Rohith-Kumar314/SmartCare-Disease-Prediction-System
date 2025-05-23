from django import forms
from django.contrib.auth.models import User
from . import models



#for admin signup
class AdminSigupForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }


#for student related form
class DoctorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class DoctorForm(forms.ModelForm):
    class Meta:
        model=models.Doctor
        fields=['address','mobile','department','status','profile_pic']



class PatientUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'email']
        widgets = {
            'password': forms.PasswordInput()
        }

class PatientForm(forms.ModelForm):
    class Meta:
        model = models.Patient
        fields = ['address', 'mobile', 'status', 'profile_pic', 'email']



# class AppointmentForm(forms.ModelForm):
#     doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
#     patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Patient Name and Symptoms", to_field_name="user_id")
#     class Meta:
#         model=models.Appointment
#         fields=['description','status']

class AppointmentForm(forms.ModelForm):
    patientId = forms.ChoiceField(
        choices=[(p.user.id, f"{p.user.first_name} {p.user.last_name} ({p.mobile if p.mobile else 'No Mobile'})") for p in models.Patient.objects.all().filter(status=True)],
        label="Patient"
    )

    class Meta:
        model = models.Appointment
        fields = ['description', 'patientId']


# class PatientAppointmentForm(forms.ModelForm):
#     doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
#     class Meta:
#         model=models.Appointment
#         fields=['description','status']

class PatientAppointmentForm(forms.ModelForm):
    class Meta:
        model = models.Appointment
        fields = ['description']  # Only description, no doctorId or status

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


import datetime
from django import forms
from .models import DoctorAvailability, DoctorLeave

class DoctorAvailabilityMultiForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Select Date"
    )
    time_slots = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        choices=[
            ('09:00', '09:00 AM'),
            ('10:00', '10:00 AM'),
            ('11:00', '11:00 AM'),
            ('12:00', '12:00 PM'),
            ('13:00', '01:00 PM'),
            ('14:00', '02:00 PM'),
            ('15:00', '03:00 PM'),
            ('16:00', '04:00 PM'),
            ('17:00', '05:00 PM'),
            ('18:00', '06:00 PM'),
            ('19:00', '07:00 PM'),
            ('20:00', '08:00 PM'),
        ],
        label="Select Time Slots"
    )

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        selected_date = kwargs.pop('selected_date', None)
        super().__init__(*args, **kwargs)
        self.error_message = ""
        if selected_date:
            self.initial['date'] = selected_date
            # Remove the date field from rendering (we use a hidden field in POST)
            self.fields.pop('date')
            # If selected date is today or in the past:
            if selected_date <= datetime.date.today():
                self.fields['time_slots'].choices = []
                self.fields['time_slots'].widget.attrs['disabled'] = True
                self.error_message = "Past dates are not allowed. Please select a future date."
            else:
                # Check if there is an approved leave for this date.
                if doctor:
                    leave_exists = DoctorLeave.objects.filter(
                        doctor=doctor,
                        status="Approved",
                        leave_start__lte=selected_date,
                        leave_end__gte=selected_date
                    ).exists()
                    if leave_exists:
                        self.fields['time_slots'].choices = []
                        self.fields['time_slots'].widget.attrs['disabled'] = True
                        self.error_message = "You have approved leave on this date. Availability cannot be set."
                    else:
                        # Compute available slots by filtering out already booked ones.
                        existing = DoctorAvailability.objects.filter(doctor=doctor, date=selected_date)
                        booked = {avail.start_time.strftime("%H:%M") for avail in existing}
                        all_choices = [
                            ('09:00', '09:00 AM'),
                            ('10:00', '10:00 AM'),
                            ('11:00', '11:00 AM'),
                            ('12:00', '12:00 PM'),
                            ('13:00', '01:00 PM'),
                            ('14:00', '02:00 PM'),
                            ('15:00', '03:00 PM'),
                            ('16:00', '04:00 PM'),
                            ('17:00', '05:00 PM'),
                            ('18:00', '06:00 PM'),
                            ('19:00', '07:00 PM'),
                            ('20:00', '08:00 PM'),
                        ]
                        available = [choice for choice in all_choices if choice[0] not in booked]
                        if not available:
                            self.error_message = "No slots available on this date."
                        self.fields['time_slots'].choices = available

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date <= datetime.date.today():
            raise forms.ValidationError("Please select a future date (at least tomorrow).")
        return date

import datetime
from django import forms
from .models import DoctorLeave

class DoctorLeaveForm(forms.ModelForm):
    class Meta:
        model = DoctorLeave
        fields = ['leave_start', 'leave_end', 'reason']
        widgets = {
            'leave_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        leave_start = cleaned_data.get('leave_start')
        leave_end = cleaned_data.get('leave_end')
        if leave_start and leave_end:
            if leave_end < leave_start:
                raise forms.ValidationError("Leave end date cannot be before leave start date.")
            if leave_start <= datetime.date.today() or leave_end <= datetime.date.today():
                raise forms.ValidationError("Both leave dates must be in the future.")
        return cleaned_data


from .models import Prescription

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicines', 'instructions', 'precautions']
        widgets = {
            'medicines': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precautions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
