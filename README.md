# Hospital Management System

A Django-based web application for managing hospital operations, including patient and doctor management, appointments, prescriptions, and disease prediction using machine learning. The system supports role-based access for admins, doctors, and patients, with secure authentication and a user-friendly interface.

## Features

- **User Management**: Secure registration and login for admins, doctors, and patients with role-based authentication.
- **Patient and Doctor CRUD**: Admins can add, update, approve, or delete patient and doctor profiles.
- **Appointment System**: Patients can book appointments with symptom-based disease prediction using NLTK and a pre-trained ML model. Doctors can view and manage appointments.
- **Prescription Management**: Doctors can issue prescriptions linked to appointments, viewable by patients.
- **Doctor Availability and Leave**: Doctors can set availability slots and apply for leaves, with admin approval.
- **Billing and Discharge**: Admins can generate and download patient discharge bills as PDFs.
- **Disease Prediction**: Symptom extraction and disease prediction using NLTK tokenization and a pickled ML model.
- **Contact Us**: Email-based contact form for user inquiries.

## Tech Stack

- **Backend**: Django, Python
- **Frontend**: HTML, CSS, JavaScript, Django Templates
- **Database**: SQLite (default, configurable to PostgreSQL)
- **Libraries**: NLTK, pandas, fuzzywuzzy, xhtml2pdf, django-widget-tweaks
- **Authentication**: Django's built-in authentication with group-based roles
- **Machine Learning**: Pre-trained model (pickled) for disease prediction

## Prerequisites

- Python 3.8+
- Django 3.0.5
- SQLite (or PostgreSQL for production)
- NLTK data (`punkt`, `punkt_tab`)

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/SmartCare-Disease-Prediction-System.git
   cd hospital-management-system
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK Data**:
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('punkt_tab')
   ```
5. **Install and Download spaCy English Model**:
   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
    ```
6. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a Superuser (Admin)**:
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://localhost:8000`.

## Usage

- **Admin**: Log in to manage doctors, patients, appointments, leaves, and discharge bills (`/adminlogin`).
- **Doctor**: Register, set availability, apply for leaves, view patients, manage appointments, and issue prescriptions (`/doctorlogin`).
- **Patient**: Register, book appointments with symptom input, view appointments, prescriptions, and discharge details (`/patientlogin`).
- **Contact Us**: Submit inquiries via the contact form (`/contactus`).

## Project Structure

- `hospitalmanagement/`: Django project settings and URLs.
- `hospital/`: Main app containing models, views, forms, and templates.
- `static/`: CSS, JavaScript, and media files.
- `templates/`: HTML templates for rendering views.
- `model/`: Pickled ML model and feature files for disease prediction.

## Notes

- The ML model (`finalized_model.sav`) and features (`features.pkl`) must be placed in the `model/` directory.
- Email functionality requires configuring `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `settings.py`.
- For production, switch to PostgreSQL and set `DEBUG = False` in `settings.py`.

## Contributing

Contributions are welcome! Please fork the repository, create a branch, and submit a pull request with your changes.

## License

This project is licensed under the MIT License.