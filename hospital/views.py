from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings
from .models import Patient, PatientPrediction
import json
import pickle
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Appointment, Patient, Doctor
from .forms import PrescriptionForm

from fuzzywuzzy import process
from difflib import get_close_matches
from nltk.tokenize import word_tokenize
from django.db.models import Prefetch

# Adding new code in doctor related views
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.messages import get_messages  # To clear old messages if needed
from . import models, forms

# New code for other functions

# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/index.html')


#for showing signup/login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/adminclick.html')


#for showing signup/login button for doctor(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')




def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request,'hospital/adminsignup.html',{'form':form})




def doctor_signup_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor=doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request,'hospital/doctorsignup.html',context=mydict)


def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    mydict = {'userForm': userForm, 'patientForm': patientForm}

    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)

        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()

            patient = patientForm.save(commit=False)
            patient.user = user
            patient.save()

            # Assign user to 'PATIENT' group
            my_patient_group, _ = Group.objects.get_or_create(name='PATIENT')
            my_patient_group.user_set.add(user)

            return HttpResponseRedirect('patientlogin')  # Redirect after successful registration

    return render(request, 'hospital/patientsignup.html', context=mydict)


#-----------for checking user is doctor , patient or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval=models.Doctor.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request,'hospital/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval=models.Patient.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request,'hospital/patient_wait_for_approval.html')
    




#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    #for both table in admin dashboard
    doctors=models.Doctor.objects.all().order_by('-id')
    patients=models.Patient.objects.all().order_by('-id')
    #for three cards
    doctorcount=models.Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount=models.Doctor.objects.all().filter(status=False).count()

    patientcount=models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount=models.Patient.objects.all().filter(status=False).count()

    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()
    mydict={
    'doctors':doctors,
    'patients':patients,
    'doctorcount':doctorcount,
    'pendingdoctorcount':pendingdoctorcount,
    'patientcount':patientcount,
    'pendingpatientcount':pendingpatientcount,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    }
    return render(request,'hospital/admin_dashboard.html',context=mydict)


# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'hospital/admin_doctor.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request,'hospital/admin_update_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'hospital/admin_add_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_doctor.html',{'doctors':doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor_specialisation.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'hospital/admin_patient.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    userForm=forms.PatientUserForm(instance=user)
    patientForm=forms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request,'hospital/admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'hospital/admin_add_patient.html',context=mydict)


#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')



#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_discharge_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    days=(date.today()-patient.admitDate) #2 days, 0:00:00
    assignedDoctor=models.User.objects.all().filter(id=patient.assignedDoctorId)
    d=days.days # only how many day that is 2
    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assignedDoctor[0].first_name,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'doctorFee':request.POST['doctorFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        #for updating to database patientDischargeDetails (pDD)
        pDD=models.PatientDischargeDetails()
        pDD.patientId=pk
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assignedDoctor[0].first_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.symptoms=patient.symptoms
        pDD.admitDate=patient.admitDate
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee=int(request.POST['doctorFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'hospital/patient_final_bill.html',context=patientDict)
    return render(request,'hospital/patient_generate_bill.html',context=patientDict)



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'patientName':dischargeDetails[0].patientName,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('hospital/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'hospital/admin_appointment.html')



# ... (Keep all existing imports and other views unchanged, including admin_add_appointment_view)

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from . import models

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments = models.Appointment.objects.filter(status=True).order_by('-appointmentDate')
    # Fetch all relevant PatientPrediction records
    patient_ids = appointments.values_list('patientId', flat=True).distinct()
    predictions = models.PatientPrediction.objects.filter(
        patient__user_id__in=patient_ids
    ).order_by('-prediction_date')
    
    # Pair appointments with predictions
    appointments_with_predictions = []
    for appointment in appointments:
        # Find matching prediction by patientId, symptoms, and date proximity
        matching_prediction = None
        for prediction in predictions:
            if (prediction.patient.user_id == appointment.patientId and
                (prediction.symptoms == appointment.symptoms or 
                 (not appointment.symptoms and not prediction.symptoms)) and
                prediction.prediction_date.date() >= appointment.appointmentDate):
                matching_prediction = prediction
                break
        appointments_with_predictions.append((appointment, matching_prediction))
    
    return render(request, 'hospital/admin_view_appointment.html', {
        'appointments_with_predictions': appointments_with_predictions
    })





from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, HttpResponseRedirect
import pandas as pd
from . import forms, models

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm = forms.AppointmentForm()
    message = None
    extracted_symptoms = None
    predicted_disease = None
    errors = None
    patient_id = None
    doctor_id = None
    description = None

    if request.method == 'POST':
        stage = request.POST.get('stage', 'submit')

        if stage == 'submit':
            appointmentForm = forms.AppointmentForm(request.POST)
            if appointmentForm.is_valid():
                description = appointmentForm.cleaned_data['description']
                patient_id = int(appointmentForm.cleaned_data['patientId'])
                patient = models.Patient.objects.get(user_id=patient_id)

                # Extract symptoms and binary vector
                try:
                    symptom_result = extract_symptoms(description)
                    detected_symptoms = symptom_result["detected_symptoms"]
                    binary_vector = symptom_result["binary_vector"]
                except Exception as e:
                    message = f"Error extracting symptoms: {str(e)}"
                    return render(request, 'hospital/admin_add_appointment.html', {
                        'appointmentForm': appointmentForm,
                        'message': message,
                        'extracted_symptoms': extracted_symptoms,
                        'predicted_disease': predicted_disease,
                        'errors': errors
                    })

                # Predict disease
                try:
                    input_df = pd.DataFrame([binary_vector], columns=feature_names)
                    input_df = input_df.infer_objects(copy=False).fillna(0).astype(int)
                    predicted_disease = loaded_model.predict(input_df)[0]
                except Exception as e:
                    message = f"Error predicting disease: {str(e)}"
                    return render(request, 'hospital/admin_add_appointment.html', {
                        'appointmentForm': appointmentForm,
                        'message': message,
                        'extracted_symptoms': extracted_symptoms,
                        'predicted_disease': predicted_disease,
                        'errors': errors
                    })

                # Prepare symptoms for display and storage
                extracted = ", ".join(sorted(detected_symptoms)) if detected_symptoms else "None"
                extracted_symptoms = extracted
                print(f"Extracted symptoms: {extracted}")
                print(f"Predicted disease: {predicted_disease}")

                # Disease to specialty mapping
                disease_specialty_map = {
                    'Stroke': 'Neurologist',
                    'Epilepsy': 'Neurologist',
                    'CAD': 'Cardiologist',
                    'Heart Failure': 'Cardiologist',
                    'Hypertensive Heart Disease': 'Cardiologist',
                    'COPD': 'Pulmonologist',
                    'Pneumonia': 'Pulmonologist',
                    'Asthma': 'Pulmonologist',
                    'Covid-19': 'Pulmonologist',
                    'Pulmonary Fibrosis': 'Pulmonologist',
                    'GERD': 'Gastroenterologist',
                    'Peptic Ulcer': 'Gastroenterologist',
                    'Gastritis': 'Gastroenterologist',
                    'Pancreatitis': 'Gastroenterologist',
                    'Hepatitis A': 'Hepatologist',
                    'Cirrhosis of Liver': 'Hepatologist',
                    'Fibrosis of Liver': 'Hepatologist',
                    'Hypoglycemia': 'Endocrinologist',
                    'Hperglycemia': 'Endocrinologist',
                    'Chronic Kidney Disease': 'Nephrologist',
                    'Acute Kidney Injury Symptoms': 'Nephrologist',
                    'Polycystic Kidney Disease': 'Nephrologist'
                }

                # Get the specialty for the predicted disease
                specialty = disease_specialty_map.get(predicted_disease, 'General Doctor')

                # Assign a doctor
                if specialty == 'General Doctor':
                    doctor = models.Doctor.objects.filter(department='General Doctor', status=True).first()
                else:
                    doctor = models.Doctor.objects.filter(department=specialty, status=True).first()
                    if not doctor:
                        doctor = models.Doctor.objects.filter(department='General Doctor', status=True).first()

                if not doctor:
                    message = "No specialized or General Doctor available. Please contact the hospital."
                    return render(request, 'hospital/admin_add_appointment.html', {
                        'appointmentForm': appointmentForm,
                        'message': message,
                        'extracted_symptoms': extracted_symptoms,
                        'predicted_disease': predicted_disease,
                        'errors': errors
                    })

                # Set assignment message
                if doctor.department == specialty:
                    message = f"Assigned to {doctor.get_name} ({specialty})."
                else:
                    message = f"No {specialty} available. Assigned to {doctor.get_name} (General Doctor)."

                doctor_id = doctor.user.id
                doctor_name = doctor.get_name
                patient_name = patient.get_name

                # Render results card
                return render(request, 'hospital/admin_add_appointment.html', {
                    'appointmentForm': appointmentForm,
                    'message': message,
                    'extracted_symptoms': extracted_symptoms,
                    'predicted_disease': predicted_disease,
                    'patient_id': patient_id,
                    'doctor_id': doctor_id,
                    'description': description,
                    'errors': errors
                })
            else:
                errors = appointmentForm.errors
                print(f"Form errors: {errors}")

        elif stage == 'confirm':
            patient_id = int(request.POST.get('patientId'))
            doctor_id = int(request.POST.get('doctorId'))
            description = request.POST.get('description')
            symptoms = request.POST.get('symptoms')
            predicted_disease = request.POST.get('predicted_disease')
            patient = models.Patient.objects.get(user_id=patient_id)
            doctor = models.Doctor.objects.get(user_id=doctor_id)
            patient_name = patient.get_name
            doctor_name = doctor.get_name

            # Save to PatientPrediction
            try:
                models.PatientPrediction.objects.create(
                    patient=patient,
                    symptoms=symptoms,
                    predicted_disease=predicted_disease
                )
            except Exception as e:
                message = f"Error saving PatientPrediction: {str(e)}"
                return render(request, 'hospital/admin_add_appointment.html', {
                    'appointmentForm': appointmentForm,
                    'message': message,
                    'extracted_symptoms': symptoms,
                    'predicted_disease': predicted_disease,
                    'patient_id': patient_id,
                    'doctor_id': doctor_id,
                    'description': description,
                    'errors': errors
                })

            # Save Appointment
            try:
                appointment = models.Appointment(
                    patientId=patient_id,
                    doctorId=doctor_id,
                    patientName=patient_name,
                    doctorName=doctor_name,
                    description=description,
                    symptoms=symptoms,
                    status=True
                )
                appointment.save()
            except Exception as e:
                message = f"Error saving Appointment: {str(e)}"
                return render(request, 'hospital/admin_add_appointment.html', {
                    'appointmentForm': appointmentForm,
                    'message': message,
                    'extracted_symptoms': symptoms,
                    'predicted_disease': predicted_disease,
                    'patient_id': patient_id,
                    'doctor_id': doctor_id,
                    'description': description,
                    'errors': errors
                })

            # Store message in session for display after redirect
            request.session['appointment_message'] = f"Appointment booked for {patient_name} with {doctor_name}."
            return HttpResponseRedirect('admin-view-appointment')

    mydict = {
        'appointmentForm': appointmentForm,
        'message': message,
        'extracted_symptoms': extracted_symptoms,
        'predicted_disease': predicted_disease,
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'description': description,
        'errors': errors
    }
    return render(request, 'hospital/admin_add_appointment.html', context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')



#--------------------- FOR Approving/Rejecting the Leave BY ADMIN START------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from hospital.models import DoctorLeave

@login_required
def admin_view_doctor_leave_requests(request):
    """View all doctor leave requests."""
    leave_requests = DoctorLeave.objects.all()
    return render(request, 'hospital/admin_view_doctor_leave_requests.html', {'leave_requests': leave_requests})

@login_required
def approve_leave(request, leave_id):
    """Approve a doctor's leave request."""
    leave_request = get_object_or_404(DoctorLeave, id=leave_id)
    leave_request.status = "Approved"
    leave_request.save()
    return redirect('admin-view-doctor-leave-requests')

@login_required
def reject_leave(request, leave_id):
    """Reject a doctor's leave request."""
    leave_request = get_object_or_404(DoctorLeave, id=leave_id)
    leave_request.status = "Rejected"
    leave_request.save()
    return redirect('admin-view-doctor-leave-requests')

#--------------------- FOR Approving/Rejecting the Leave BY ADMIN END-----------------


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#-------------------------------------
# --------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    # patientcount=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).count()
    patientcount=models.Patient.objects.all().filter(status=True).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_patient.html',context=mydict)



from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from hospital import models
from .models import Patient, Appointment, PatientPrediction, Prescription
from django.db.models import Prefetch

def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(
        doctorId=request.user.id,
        status=True
    ).prefetch_related(
        Prefetch(
            'prescription_set',
            queryset=models.Prescription.objects.order_by('-prescribed_date')
        )
    )
    patient_ids = appointments.values_list('patientId', flat=True)
    patients = models.Patient.objects.filter(
        user_id__in=patient_ids
    ).prefetch_related(
        Prefetch(
            'patientprediction_set',
            queryset=models.PatientPrediction.objects.order_by('-prediction_date')
        )
    )
    patient_dict = {patient.user_id: patient for patient in patients}
    appointment_data = []
    for appointment in appointments:
        patient = patient_dict.get(appointment.patientId)
        appointment_data.append({
            'appointment': appointment,
            'patient': patient,
            'predictions': patient.patientprediction_set.all() if patient else [],
            'prescriptions': appointment.prescription_set.all()
        })
    return render(request, 'hospital/doctor_view_patient.html', {
        'appointment_data': appointment_data,
        'doctor': doctor
    })


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})



@login_required(login_url='doctorlogin')
def doctor_view_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    
    # Fetch all confirmed appointments for this doctor
    appointments = models.Appointment.objects.filter(status=True, doctorId=request.user.id)

    # Fetch patient details
    patient_ids = [a.patientId for a in appointments]
    patients = models.Patient.objects.filter(status=True, user_id__in=patient_ids)

    # Create a mapping for predictions (Latest prediction per patient)
    patient_predictions = {p.user_id: models.PatientPrediction.objects.filter(patient=p).order_by('-prediction_date').first() for p in patients}

    # Prepare data for rendering
    appointment_data = []
    for appointment, patient in zip(appointments, patients):
        predicted_disease = patient_predictions.get(patient.user_id, None)
        appointment_data.append({
            'appointment': appointment,
            'patient': patient,
            'predicted_disease': predicted_disease.predicted_disease if predicted_disease else "Not Available"
        })

    return render(request, 'hospital/doctor_view_appointment.html', {'appointments': appointment_data, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})

#  for adding Prescription for the patient



def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def prescribe_medicine(request, appointment_id):
    try:
        # Get the appointment instance
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Fetch patient and doctor using user_id
        patient = get_object_or_404(Patient, user_id=appointment.patientId)
        doctor = get_object_or_404(Doctor, user_id=appointment.doctorId)

        if request.method == 'POST':
            form = PrescriptionForm(request.POST)
            if form.is_valid():
                prescription = form.save(commit=False)
                prescription.patient = patient
                prescription.doctor = doctor
                prescription.appointment = appointment
                prescription.save()
                
                messages.success(request, "Prescription Added Successfully!")  
                return redirect('doctor-view-appointment')  
            else:
                messages.error(request, "Error adding prescription. Please check the form.")

        else:
            form = PrescriptionForm()

        return render(request, 'hospital/doctor_prescribe_medicine.html', {  
            'form': form,
            'patient': patient,
            'appointment': appointment
        })

    except Exception as e:
        messages.error(request, f"Unexpected error: {str(e)}")  
        return redirect('doctor-view-appointment')
   
    


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_set_availability_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    
    # Clear any lingering messages from previous pages
    list(get_messages(request))

    selected_date = None
    if request.method == "GET":
        if 'date' in request.GET:
            try:
                selected_date = datetime.datetime.strptime(request.GET.get('date'), "%Y-%m-%d").date()
                if selected_date <= datetime.date.today():
                    messages.error(request, "Please select a future date (at least tomorrow).")
                    selected_date = None  # Do not load any time slots
            except Exception:
                messages.error(request, "Invalid date format.")
                selected_date = None
        form = forms.DoctorAvailabilityMultiForm(doctor=doctor, selected_date=selected_date)
    else:  # POST request
        try:
            selected_date = datetime.datetime.strptime(request.POST.get('date'), "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Invalid date format.")
            return redirect("doctor_set_availability")
        form = forms.DoctorAvailabilityMultiForm(request.POST, doctor=doctor, selected_date=selected_date)
        if form.is_valid():
            # Double-check for approved leave
            leave_exists = models.DoctorLeave.objects.filter(
                doctor=doctor,
                status="Approved",
                leave_start__lte=selected_date,
                leave_end__gte=selected_date
            ).exists()
            if leave_exists:
                messages.error(request, "You have approved leave on this date. Availability cannot be set.")
                return redirect("doctor_set_availability")
            time_slots = form.cleaned_data.get('time_slots')
            if not time_slots:
                messages.error(request, "No available time slots on this date. Please select a different date.")
                return redirect("doctor_set_availability")
            for slot in time_slots:
                start_time = datetime.datetime.strptime(slot, "%H:%M").time()
                dt = datetime.datetime.combine(selected_date, start_time)
                end_time = (dt + datetime.timedelta(hours=1)).time()
                models.DoctorAvailability.objects.create(
                    doctor=doctor,
                    date=selected_date,
                    start_time=start_time,
                    end_time=end_time
                )
            messages.success(request, "Availability set successfully!")
            return redirect("doctor_set_availability")
    context = {"form": form, "doctor": doctor}
    return render(request, "hospital/doctor_set_availability.html", context)


# Doctor leave
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_apply_leave_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    if request.method == "POST":
        form = forms.DoctorLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.doctor = doctor
            leave.save()
            messages.success(request, "Leave applied successfully! Please wait for admin approval.")
            return redirect("doctor_apply_leave")
    else:
        form = forms.DoctorLeaveForm()
    context = {"form": form, "doctor": doctor}
    return render(request, "hospital/doctor_apply_leave.html", context)




#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    # doctor=models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    # doctor = patient.doctor if patient.doctor else None
    # newly Added code
    latest_appointment = models.Appointment.objects.filter(patientId=patient.user_id).order_by('-id').first()
    
    if latest_appointment:
        doctor = models.Doctor.objects.get(user_id=latest_appointment.doctorId)
    else:
        doctor = None  # No doctor assigned yet
    # old code
    mydict={
        'patient': patient,
        'doctorName': doctor.get_name if doctor else "Not Assigned",
        'doctorMobile': doctor.mobile if doctor else "N/A",
        'doctorAddress': doctor.address if doctor else "N/A",
        'doctorDepartment': doctor.department if doctor else "N/A",
        'admitDate': patient.admitDate,
        'symptoms': latest_appointment.symptoms if latest_appointment else "No symptoms recorded",
    }
    return render(request,'hospital/patient_dashboard.html',context=mydict)





@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})




# # --- Symptom Normalization via synonyms + fuzzy match ---
# def get_synonyms(word):
#     synonyms = set()
#     for syn in wordnet.synsets(word.replace("_", " ")):
#         for lemma in syn.lemmas():
#             synonyms.add(lemma.name().lower().replace(" ", "_"))
#     return synonyms





import re
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from nltk.tokenize import word_tokenize
from fuzzywuzzy import fuzz
from . import forms, models
import nltk
import spacy
import pandas as pd
import pickle
from collections import defaultdict


# Load spaCy model (free, open-source)
nlp = spacy.load("en_core_web_sm")

# Load model and features
MODEL_PATH = "model/finalized_model.sav"
FEATURES_PATH = "model/features.pkl"

with open(FEATURES_PATH, 'rb') as f:
    feature_names = pickle.load(f)
    feature_names_list = list(feature_names)  # Convert to list

# Use feature_names as SYMPTOMS_LIST
SYMPTOMS_LIST = sorted(list(set(feature_names)))

# Map duplicates to canonical symptoms
SYMPTOM_MAPPING = {
    'headache.1': 'headache', 'headache.2': 'headache', 'headache.3': 'headache',
    'headaches': 'headache', 'headaches.1': 'headache',
    'chest_pain.1': 'chest_pain', 'chest_pain.2': 'chest_pain', 'chest_pain.3': 'chest_pain',
    'chest pain': 'chest_pain', 'chest pain.1': 'chest_pain', 'chest pain.2': 'chest_pain',
    'chest pain.3': 'chest_pain',
    'dizziness.1': 'dizziness', 'dizziness.2': 'dizziness', 'dizziness ': 'dizziness',
    'diarrhoea.1': 'diarrhoea', 'diarrhoea.2': 'diarrhoea', 'diarrhoea.3': 'diarrhoea',
    'sweating.1': 'sweating', 'sweatings.1': 'sweatings',
    'fever.1': 'fever', 'fever ': 'fever',
    'low_grade_fever.1': 'low_grade_fever',
    'loss_of_appetite.1': 'loss_of_appetite', 'loss_of_appetite.2': 'loss_of_appetite',
    'loss_of_appetite.3': 'loss_of_appetite', 'loss_of_appetite.4': 'loss_of_appetite',
    'loss_of_appetite.5': 'loss_of_appetite',
    'edema.1': 'edema',
    'jaundice.1': 'jaundice', 'jaundice.2': 'jaundice',
    'itching.1': 'itching', 'ictching.1': 'itching',
    'weakness.1': 'weakness', 'weakness.2': 'weakness',
    'discomfort.1': 'discomfort', 'discomfort ': 'discomfort',
    'anxiety.1': 'anxiety',
    'fainting.1': 'fainting',
    'bloating.1': 'bloating', 'bloating.2': 'bloating',
    'wheezing ': 'wheezing',
    'cough.1': 'cough',
    'slurred_speech.1': 'slurred_speech',
    'dark_urine': 'dark_urine', 'ascites ': 'ascites',
    'tiredness': 'unusual_tiredness', 'unusual_tiredness ': 'unusual_tiredness',
    'high_blood_pressure': 'hypertension', 'hypertension ': 'hypertension',
    'blood_in_your_urine': 'blood_in_your_urine',
    'arm_or_leg unable to rise': 'arm_or_leg_unable_to_rise',
    'numbness ': 'numbness'
}

loaded_model = pickle.load(open(MODEL_PATH, 'rb'))

# Build symptom keyword dictionary (no WordNet)
symptom_keywords = defaultdict(list)
for symptom in feature_names:
    canonical = SYMPTOM_MAPPING.get(symptom, symptom)
    phrase = canonical.replace("_", " ")
    symptom_keywords[symptom].append(phrase)

# Manual medical synonyms (expanded for precision)
manual_synonyms = {
    'headache': ['pain in head', 'migraine', 'head ache', 'head pain'],
    'dizziness': ['dizzy', 'lightheadedness', 'vertigo', 'feeling dizzy'],
    'sweatings': ['sweating', 'perspiration'],
    'chest_pain': ['pain in chest', 'chest ache', 'chest pain'],
    'trouble_in_walking': ['difficulty walking', 'can’t walk properly', 'cant walk properly', 'cannot walk properly', 'walk difficulty', 'trouble walking'],
    'fever': ['high temperature', 'feverish'],
    'nausea': ['feeling sick', 'queasy', 'nauseous'],
    'fatigue': ['exhaustion', 'feeling tired'],
    'shortness_of_breath': ['breathlessness', 'difficulty breathing'],
    'cough': ['coughing'],
    'diarrhoea': ['diarrhea', 'loose stools'],
    'chest_tightness': ['tight chest'],
    'joint_pain': ['pain in joints'],
    'abdominal_pain': ['stomach pain', 'belly ache'],
    'trouble_speaking': ['speech difficulty', 'can’t talk properly'],
    'numbness': ['tingling', 'numb feeling', 'numbness'],
    'arm_or_leg_unable_to_rise': ['unable to lift hands', 'unable to lift legs', 'can’t raise arms', 'can’t raise legs', 'unable lift hands or legs']
}
if 'fatigue' in feature_names:
    manual_synonyms['fatigue'] = ['exhaustion', 'feeling tired']

for symptom, synonyms in manual_synonyms.items():
    for orig_symptom in feature_names:
        if SYMPTOM_MAPPING.get(orig_symptom, orig_symptom) == symptom:
            symptom_keywords[orig_symptom].extend(synonyms)

# Negation words
NEGATION_WORDS = {'no', 'not', 'never', 'don’t', 'doesn’t', 'didn’t', 'none', 'without'}

def correct_spelling(text):
    """
    Correct spelling mistakes using fuzzy matching against symptom keywords.
    """
    # Normalize 'cant' to 'can’t'
    text = text.replace("cant", "can’t")
    words = nltk.word_tokenize(text.lower())
    corrected_words = []
    
    for word in words:
        best_match, score = None, 0
        for symptom, keywords in symptom_keywords.items():
            for keyword in keywords:
                current_score = fuzz.ratio(word, keyword)
                if current_score > score and current_score >= 90:
                    score = current_score
                    best_match = keyword
        corrected_words.append(best_match if best_match else word)
    
    return " ".join(corrected_words)

def detect_negations(description):
    """
    Identify negated symptoms to avoid false positives.
    """
    negated_symptoms = set()
    sentences = nltk.sent_tokenize(description.lower())
    
    for sentence in sentences:
        doc = nlp(sentence)
        tokens = [token.text for token in doc]
        
        for i, token in enumerate(tokens):
            if token in NEGATION_WORDS:
                for j in range(i + 1, min(i + 4, len(tokens))):
                    phrase = " ".join(tokens[i + 1:j + 1])
                    for symptom, keywords in symptom_keywords.items():
                        if any(fuzz.ratio(phrase, kw) >= 95 for kw in keywords):
                            negated_symptoms.add(symptom)
                            break
    
    return negated_symptoms

def extract_symptoms(description):
    """
    Extract symptoms and return binary vector and symptom list.
    """
    # Preprocess
    description = description.replace("-", " ")
    corrected_description = correct_spelling(description)
    description_lower = corrected_description.lower()
    doc = nlp(description_lower)
    
    # Detect negations
    negated_symptoms = detect_negations(description_lower)
    
    # Initialize outputs
    detected_symptoms = set()
    binary_vector = [0] * len(feature_names_list)
    
    # Rule-based matching (exact and near-exact)
    for i, symptom in enumerate(feature_names_list):
        for keyword in symptom_keywords[symptom]:
            if re.search(r'\b' + re.escape(keyword) + r'\b', description_lower) or \
               any(fuzz.ratio(keyword, chunk.text.lower()) >= 85 for chunk in doc.noun_chunks):
                if symptom not in negated_symptoms:
                    detected_symptoms.add(symptom)
                    binary_vector[i] = 1
    
    # Phrase-based fuzzy matching (for multi-word symptoms)
    tokens = description_lower.split()
    for i in range(len(tokens)):
        for j in range(i + 1, min(i + 5, len(tokens) + 1)):
            phrase = " ".join(tokens[i:j])
            for symptom, keywords in symptom_keywords.items():
                if symptom not in detected_symptoms:
                    for keyword in keywords:
                        if fuzz.ratio(phrase, keyword) >= 85:
                            if symptom not in negated_symptoms:
                                detected_symptoms.add(symptom)
                                binary_vector[feature_names_list.index(symptom)] = 1
                                break
    
    # Contextual matching with spaCy (noun chunks and verb phrases)
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        if len(chunk_text.split()) > 4:
            continue
        for symptom, keywords in symptom_keywords.items():
            if symptom not in detected_symptoms:
                for keyword in keywords:
                    if fuzz.ratio(chunk_text, keyword) >= 85:
                        context_words = {
                            'headache': ['head'],
                            'chest_pain': ['chest'],
                            'dizziness': ['dizzy'],
                            'arm_or_leg_unable_to_rise': ['arm', 'leg', 'hands', 'legs'],
                            'numbness': ['numb', 'tingling'],
                            'trouble_in_walking': ['walk', 'walking', 'difficulty', 'properly'],
                            'fever': ['fever', 'temperature'],
                            'diarrhoea': ['stool', 'stools', 'diarrhea']
                        }
                        if symptom in context_words:
                            if any(cw in description_lower for cw in context_words[symptom]):
                                if symptom not in negated_symptoms:
                                    detected_symptoms.add(symptom)
                                    binary_vector[feature_names_list.index(symptom)] = 1
                                    break
                        else:
                            if symptom not in negated_symptoms:
                                detected_symptoms.add(symptom)
                                binary_vector[feature_names_list.index(symptom)] = 1
                                break
    
    # Verb phrase matching for symptoms like 'trouble_in_walking'
    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                verb_phrase = " ".join([t.text for t in token.subtree if t.pos_ in ["VERB", "ADV", "PART"]])
                for symptom, keywords in symptom_keywords.items():
                    if symptom not in detected_symptoms:
                        for keyword in keywords:
                            if fuzz.ratio(verb_phrase, keyword) >= 85:
                                context_words = {
                                    'trouble_in_walking': ['walk', 'walking', 'difficulty', 'properly']
                                }
                                if symptom in context_words:
                                    if any(cw in description_lower for cw in context_words[symptom]):
                                        if symptom not in negated_symptoms:
                                            detected_symptoms.add(symptom)
                                            binary_vector[feature_names_list.index(symptom)] = 1
                                            break
                                else:
                                    if symptom not in negated_symptoms:
                                        detected_symptoms.add(symptom)
                                        binary_vector[feature_names_list.index(symptom)] = 1
                                        break
    
    # Normalize duplicates
    canonical_symptoms = set()
    for symptom in detected_symptoms:
        canonical = SYMPTOM_MAPPING.get(symptom, symptom)
        canonical_symptoms.add(canonical)
    
    return {
        "detected_symptoms": canonical_symptoms,
        "binary_vector": binary_vector
    }

# Role check
def is_patient(user):
    return models.Patient.objects.filter(user_id=user.id).exists()

# Main view
# @login_required(login_url='patientlogin')
# @user_passes_test(is_patient)
# def patient_book_appointment_view(request):
#     appointmentForm = forms.PatientAppointmentForm()
#     patient = models.Patient.objects.get(user_id=request.user.id)
#     message = None
#     extracted_symptoms = None

#     if request.method == 'POST':
#         appointmentForm = forms.PatientAppointmentForm(request.POST)
#         if appointmentForm.is_valid():
#             desc = request.POST.get('description', '')

#             # Extract symptoms and binary vector
#             symptom_result = extract_symptoms(desc)
#             detected_symptoms = symptom_result["detected_symptoms"]
#             binary_vector = symptom_result["binary_vector"]
            
#             # Predict disease
#             input_df = pd.DataFrame([binary_vector], columns=feature_names)
#             input_df = input_df.infer_objects(copy=False).fillna(0).astype(int)
#             predicted_disease = loaded_model.predict(input_df)[0]
            
#             # Prepare symptoms for display and storage
#             extracted = ", ".join(sorted(detected_symptoms)) if detected_symptoms else "None"
#             extracted_symptoms = extracted
#             print(f"Extracted symptoms: {extracted}")
#             print(f"Predicted disease: {predicted_disease}")

#             # Save to PatientPrediction
#             models.PatientPrediction.objects.create(
#                 patient=patient,
#                 symptoms=extracted,
#                 predicted_disease=predicted_disease
#             )

#             # Save Appointment
#             appointment = appointmentForm.save(commit=False)
#             appointment.doctorId = request.POST.get('doctorId')
#             appointment.patientId = request.user.id
#             appointment.doctorName = models.User.objects.get(id=request.POST.get('doctorId')).first_name
#             appointment.patientName = request.user.first_name
#             appointment.symptoms = extracted
#             appointment.status = False
#             appointment.save()

#             return HttpResponseRedirect('patient-view-appointment')

#     mydict = {
#         "appointmentForm": appointmentForm,
#         "patient": patient,
#         "message": message,
#         "extracted_symptoms": extracted_symptoms
#     }
#     return render(request, 'hospital/patient_book_appointment.html', context=mydict)

# ... (Keep all existing imports, symptom extraction, and other code unchanged)

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm = forms.PatientAppointmentForm()
    patient = models.Patient.objects.get(user_id=request.user.id)
    message = None
    extracted_symptoms = None
    predicted_disease = None

    if request.method == 'POST':
        appointmentForm = forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            desc = request.POST.get('description', '')

            # Extract symptoms and binary vector
            symptom_result = extract_symptoms(desc)
            detected_symptoms = symptom_result["detected_symptoms"]
            binary_vector = symptom_result["binary_vector"]
            
            # Predict disease
            input_df = pd.DataFrame([binary_vector], columns=feature_names)
            input_df = input_df.infer_objects(copy=False).fillna(0).astype(int)
            predicted_disease = loaded_model.predict(input_df)[0]
            
            # Prepare symptoms for display and storage
            extracted = ", ".join(sorted(detected_symptoms)) if detected_symptoms else "None"
            extracted_symptoms = extracted
            print(f"Extracted symptoms: {extracted}")
            print(f"Predicted disease: {predicted_disease}")

            # Disease to specialty mapping
            disease_specialty_map = {
                'Stroke': 'Neurologist',
                'Epilepsy': 'Neurologist',
                'CAD': 'Cardiologist',
                'Heart Failure': 'Cardiologist',
                'Hypertensive Heart Disease': 'Cardiologist',
                'COPD': 'Pulmonologist',
                'Pneumonia': 'Pulmonologist',
                'Asthma': 'Pulmonologist',
                'Covid-19': 'Pulmonologist',
                'Pulmonary Fibrosis': 'Pulmonologist',
                'GERD': 'Gastroenterologist',
                'Peptic Ulcer': 'Gastroenterologist',
                'Gastritis': 'Gastroenterologist',
                'Pancreatitis': 'Gastroenterologist',
                'Hepatitis A': 'Hepatologist',
                'Cirrhosis of Liver': 'Hepatologist',
                'Fibrosis of Liver': 'Hepatologist',
                'Hypoglycemia': 'Endocrinologist',
                'Hperglycemia': 'Endocrinologist',
                'Chronic Kidney Disease': 'Nephrologist',
                'Acute Kidney Injury Symptoms': 'Nephrologist',
                'Polycystic Kidney Disease': 'Nephrologist'
            }

            # Get the specialty for the predicted disease
            specialty = disease_specialty_map.get(predicted_disease, 'General Doctor')  # Fallback to General Doctor

            # Assign a doctor
            if specialty == 'General Doctor':
                doctor = models.Doctor.objects.filter(department='General Doctor', status=True).first()
            else:
                doctor = models.Doctor.objects.filter(department=specialty, status=True).first()
                if not doctor:
                    # Fallback to General Doctor
                    doctor = models.Doctor.objects.filter(department='General Doctor', status=True).first()

            if not doctor:
                # No specialized or General Doctor available
                message = "No specialized or General Doctor available. Please contact the hospital."
                return render(request, 'hospital/patient_book_appointment.html', {
                    'appointmentForm': appointmentForm,
                    'patient': patient,
                    'message': message,
                    'extracted_symptoms': extracted_symptoms,
                    'predicted_disease': predicted_disease
                })

            # Set assignment message
            if doctor.department == specialty:
                message = f"Assigned to {doctor.get_name} ({specialty})."
            else:
                message = f"No {specialty} available. Assigned to {doctor.get_name} (General Doctor)."

            doctor_id = doctor.user.id
            doctor_name = doctor.get_name

            # Save to PatientPrediction
            models.PatientPrediction.objects.create(
                patient=patient,
                symptoms=extracted,
                predicted_disease=predicted_disease
            )

            # Save Appointment
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = doctor_id
            appointment.patientId = request.user.id
            appointment.doctorName = doctor_name
            appointment.patientName = request.user.first_name
            appointment.symptoms = extracted
            appointment.status = True
            appointment.save()

            return render(request, 'hospital/patient_book_appointment.html', {
                'appointmentForm': appointmentForm,
                'patient': patient,
                'message': message,
                'extracted_symptoms': extracted_symptoms,
                'predicted_disease': predicted_disease
            })

    mydict = {
        'appointmentForm': appointmentForm,
        'patient': patient,
        'message': message,
        'extracted_symptoms': extracted_symptoms,
        'predicted_disease': predicted_disease
    }
    return render(request, 'hospital/patient_book_appointment.html', context=mydict)

# ... (Keep all other views unchanged: patient_view_appointment_view, patient_discharge_view, patient_view_prescription)




# ... (Keep all existing imports and other views unchanged)

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from . import models

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(patientId=request.user.id).order_by('-appointmentDate')
    predictions = models.PatientPrediction.objects.filter(patient=patient).order_by('-prediction_date')
    
    # Pair appointments with predictions based on symptoms and date proximity
    appointments_with_predictions = []
    for appointment in appointments:
        # Find matching prediction by symptoms and closest date
        matching_prediction = None
        for prediction in predictions:
            if (prediction.symptoms == appointment.symptoms or 
                (not appointment.symptoms and not prediction.symptoms)) and \
               prediction.prediction_date.date() >= appointment.appointmentDate:
                matching_prediction = prediction
                break
        appointments_with_predictions.append((appointment, matching_prediction))
    
    return render(request, 'hospital/patient_view_appointment.html', {
        'appointments_with_predictions': appointments_with_predictions,
        'patient': patient
    })


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'hospital/patient_discharge.html',context=patientDict)



# for viewing the prescription
from hospital.models import Prescription, Patient
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_prescription(request):
    # Fetch the logged-in patient
    patient = get_object_or_404(Patient, user_id=request.user.id)
    
    # Fetch prescriptions related to the patient
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-prescribed_date')

    return render(request, 'hospital/patient_view_prescription.html', {
        'patient': patient,
        'prescriptions': prescriptions
    })


#--------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------


#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
# ---------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form':sub})
