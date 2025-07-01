from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from django.http import HttpResponseServerError
import traceback

from django.contrib.auth.views import LoginView

class AdminLoginView(LoginView):
    template_name = 'school/adminlogin.html'

class TeacherLoginView(LoginView):
    template_name = 'school/teacherlogin.html'

class StudentLoginView(LoginView):
    template_name = 'school/studentlogin.html'


User = get_user_model()

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'school/index.html')

# Authentication views
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'school/adminclick.html')

def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'school/teacherclick.html')

def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'school/studentclick.html')

def admin_signup_view(request):
    form = forms.AdminSignupForm()
    if request.method == 'POST':
        form = forms.AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            admin_group, created = Group.objects.get_or_create(name='ADMIN')
            admin_group.user_set.add(user)
            
            return HttpResponseRedirect('adminlogin')
    return render(request, 'school/adminsignup.html', {'form': form})

def student_signup_view(request):
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()
    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user = form1.save(commit=False)
            user.set_password(form1.cleaned_data['password1'])
            user.save()
            
            student = form2.save(commit=False)
            student.user = user
            student.save()
            
            student_group, created = Group.objects.get_or_create(name='STUDENT')
            student_group.user_set.add(user)
            return HttpResponseRedirect('studentlogin')
    return render(request, 'school/studentsignup.html', {'form1': form1, 'form2': form2})

def teacher_signup_view(request):
    form1 = forms.TeacherUserForm()
    form2 = forms.TeacherExtraForm()
    if request.method == 'POST':
        form1 = forms.TeacherUserForm(request.POST)
        form2 = forms.TeacherExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user = form1.save(commit=False)
            user.set_password(form1.cleaned_data['password1'])
            user.save()
            
            teacher = form2.save(commit=False)
            teacher.user = user
            teacher.save()
            
            teacher_group, created = Group.objects.get_or_create(name='TEACHER')
            teacher_group.user_set.add(user)
            return HttpResponseRedirect('teacherlogin')
    return render(request, 'school/teachersignup.html', {'form1': form1, 'form2': form2})

# Group check functions
def is_admin(user):
    return user.is_staff

def is_teacher(user):
    return models.TeacherExtra.objects.filter(user=user).exists()


def is_student(user):
    return models.StudentExtra.objects.filter(user=user).exists()


from django.http import HttpResponse

from django.shortcuts import redirect
from . import models

def afterlogin_view(request):
    user = request.user

    if is_admin(user):
        return redirect('admin-dashboard')

    elif is_teacher(user):
        approved = models.TeacherExtra.objects.filter(user=user, status=True).exists()
        if approved:
            return redirect('teacher-dashboard')
        return redirect('teacher-waiting-approval')  # this should exist

    elif is_student(user):
        approved = models.StudentExtra.objects.filter(user=user, status=True).exists()
        if approved:
            return redirect('student-dashboard')
        return redirect('student-waiting-approval')  # this should exist

    return redirect('home')

# Admin Dashboard
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    teacher_count = models.TeacherExtra.objects.filter(status=True).count()
    pending_teacher_count = models.TeacherExtra.objects.filter(status=False).count()
    
    student_count = models.StudentExtra.objects.filter(status=True).count()
    pending_student_count = models.StudentExtra.objects.filter(status=False).count()
    
    teacher_salary = models.TeacherExtra.objects.filter(status=True).aggregate(Sum('salary'))['salary__sum'] or 0
    pending_teacher_salary = models.TeacherExtra.objects.filter(status=False).aggregate(Sum('salary'))['salary__sum'] or 0
    
    student_fee = models.StudentExtra.objects.filter(status=True).aggregate(Sum('fee'))['fee__sum'] or 0
    pending_student_fee = models.StudentExtra.objects.filter(status=False).aggregate(Sum('fee'))['fee__sum'] or 0
    
    notices = models.Notice.objects.all()
    
    context = {
        'teachercount': teacher_count,
        'pendingteachercount': pending_teacher_count,
        'studentcount': student_count,
        'pendingstudentcount': pending_student_count,
        'teachersalary': teacher_salary,
        'pendingteachersalary': pending_teacher_salary,
        'studentfee': student_fee,
        'pendingstudentfee': pending_student_fee,
        'notice': notices
    }
    return render(request, 'school/admin_dashboard.html', context)

# Admin Teacher Management
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_teacher_view(request):
    return render(request, 'school/admin_teacher.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_teacher_view(request):
    if request.method == 'POST':
        form1 = forms.TeacherUserForm(request.POST)
        form2 = forms.TeacherExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user = form1.save(commit=False)
            user.set_password(form1.cleaned_data['password1'])
            user.save()
            
            teacher = form2.save(commit=False)
            teacher.user = user
            teacher.status = True
            teacher.save()
            
            teacher_group, created = Group.objects.get_or_create(name='TEACHER')
            teacher_group.user_set.add(user)
            return redirect('admin-teacher')
    else:
        form1 = forms.TeacherUserForm()
        form2 = forms.TeacherExtraForm()
    return render(request, 'school/admin_add_teacher.html', {'form1': form1, 'form2': form2})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_teacher_view(request):
    teachers = models.TeacherExtra.objects.filter(status=True)
    return render(request, 'school/admin_view_teacher.html', {'teachers': teachers})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_teacher_view(request):
    teachers = models.TeacherExtra.objects.filter(status=False)
    return render(request, 'school/admin_approve_teacher.html', {'teachers': teachers})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_teacher_view(request, pk):
    teacher = models.TeacherExtra.objects.get(id=pk)
    teacher.status = True
    teacher.save()
    return redirect('admin-approve-teacher')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_teacher_view(request, pk):
    teacher = models.TeacherExtra.objects.get(id=pk)
    teacher.user.delete()
    teacher.delete()
    return redirect('admin-approve-teacher')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_teacher_from_school_view(request, pk):
    teacher = models.TeacherExtra.objects.get(id=pk)
    teacher.user.delete()
    teacher.delete()
    return redirect('admin-view-teacher')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_teacher_view(request, pk):
    teacher = models.TeacherExtra.objects.get(id=pk)
    user = teacher.user
    
    if request.method == 'POST':
        form1 = forms.TeacherUserForm(request.POST, instance=user)
        form2 = forms.TeacherExtraForm(request.POST, instance=teacher)
        if form1.is_valid() and form2.is_valid():
            user = form1.save(commit=False)
            if form1.cleaned_data.get('password'):
                user.set_password(form1.cleaned_data['password'])
            user.save()
            form2.save()
            return redirect('admin-view-teacher')
    else:
        form1 = forms.TeacherUserForm(instance=user)
        form2 = forms.TeacherExtraForm(instance=teacher)
    
    return render(request, 'school/admin_update_teacher.html', {'form1': form1, 'form2': form2})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_teacher_salary_view(request):
    teachers = models.TeacherExtra.objects.all()
    return render(request, 'school/admin_view_teacher_salary.html', {'teachers': teachers})

# Admin Student Management
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_student_view(request):
    return render(request, 'school/admin_student.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_student_view(request):
    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user = form1.save(commit=False)
            user.set_password(form1.cleaned_data['password1'])
            user.save()
            
            student = form2.save(commit=False)
            student.user = user
            student.status = True
            student.save()
            
            student_group, created = Group.objects.get_or_create(name='STUDENT')
            student_group.user_set.add(user)
            return redirect('admin-student')
    else:
        form1 = forms.StudentUserForm()
        form2 = forms.StudentExtraForm()
    return render(request, 'school/admin_add_student.html', {'form1': form1, 'form2': form2})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_student_view(request):
    students = models.StudentExtra.objects.filter(status=True)
    return render(request, 'school/admin_view_student.html', {'students': students})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_student_from_school_view(request, pk):
    student = models.StudentExtra.objects.get(id=pk)
    student.user.delete()
    student.delete()
    return redirect('admin-view-student')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_student_view(request, pk):
    student = models.StudentExtra.objects.get(id=pk)
    student.user.delete()
    student.delete()
    return redirect('admin-approve-student')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_student_view(request, pk):
    student = models.StudentExtra.objects.get(id=pk)
    user = student.user
    
    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST, instance=user)
        form2 = forms.StudentExtraForm(request.POST, instance=student)
        if form1.is_valid() and form2.is_valid():
            user = form1.save(commit=False)
            if form1.cleaned_data.get('password'):
                user.set_password(form1.cleaned_data['password'])
            user.save()
            form2.save()
            return redirect('admin-view-student')
    else:
        form1 = forms.StudentUserForm(instance=user)
        form2 = forms.StudentExtraForm(instance=student)
    
    return render(request, 'school/admin_update_student.html', {'form1': form1, 'form2': form2})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_student_view(request):
    students = models.StudentExtra.objects.filter(status=False)
    return render(request, 'school/admin_approve_student.html', {'students': students})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_student_view(request, pk):
    student = models.StudentExtra.objects.get(id=pk)
    student.status = True
    student.save()
    return redirect('admin-approve-student')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_student_fee_view(request):
    students = models.StudentExtra.objects.all()
    return render(request, 'school/admin_view_student_fee.html', {'students': students})

# Attendance Management
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_attendance_view(request):
    return render(request, 'school/admin_attendance.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_take_attendance_view(request, cl):
    students = models.StudentExtra.objects.filter(cl=cl, status=True)
    if request.method == 'POST':
        form = forms.AttendanceForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            for student in students:
                status = request.POST.get(f'status_{student.id}')
                if status:
                    attendance, created = models.Attendance.objects.update_or_create(
                        roll=student.roll,
                        cl=cl,
                        date=date,
                        defaults={'present_status': status}
                    )
            return redirect('admin-attendance')
    else:
        form = forms.AttendanceForm()
    return render(request, 'school/admin_take_attendance.html', {'students': students, 'form': form, 'cl': cl})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_attendance_view(request, cl):
    if request.method == 'POST':
        form = forms.AskDateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            attendance_data = models.Attendance.objects.filter(date=date, cl=cl)
            student_data = models.StudentExtra.objects.filter(cl=cl)
            return render(request, 'school/admin_view_attendance_page.html', {
                'cl': cl,
                'attendance_data': attendance_data,
                'student_data': student_data,
                'date': date
            })
    else:
        form = forms.AskDateForm()
    return render(request, 'school/admin_view_attendance_ask_date.html', {'cl': cl, 'form': form})

# Fee Management
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_fee_view(request):
    return render(request, 'school/admin_fee.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_fee_view(request, cl):
    fee_details = models.StudentExtra.objects.filter(cl=cl, status=True)
    return render(request, 'school/admin_view_fee.html', {'feedetails': fee_details, 'cl': cl})

# Notice Management
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_notice_view(request):
    if request.method == 'POST':
        form = forms.NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.by = request.user.first_name
            notice.save()
            return redirect('admin-dashboard')
    else:
        form = forms.NoticeForm()
    return render(request, 'school/admin_notice.html', {'form': form})

# Teacher Dashboard
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    teacher_data = models.TeacherExtra.objects.get(user=request.user, status=True)
    notices = models.Notice.objects.all()
    context = {
        'salary': teacher_data.salary,
        'mobile': teacher_data.mobile,
        'date': teacher_data.joindate,
        'notice': notices
    }
    return render(request, 'school/teacher_dashboard.html', context)

# Teacher Attendance
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_attendance_view(request):
    return render(request, 'school/teacher_attendance.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_take_attendance_view(request, cl):
    students = models.StudentExtra.objects.filter(cl=cl, status=True)
    if request.method == 'POST':
        form = forms.AttendanceForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            for student in students:
                status = request.POST.get(f'status_{student.id}')
                if status:
                    attendance, created = models.Attendance.objects.update_or_create(
                        roll=student.roll,
                        cl=cl,
                        date=date,
                        defaults={'present_status': status}
                    )
            return redirect('teacher-attendance')
    else:
        form = forms.AttendanceForm()
    return render(request, 'school/teacher_take_attendance.html', {'students': students, 'form': form, 'cl': cl})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_attendance_view(request, cl):
    if request.method == 'POST':
        form = forms.AskDateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            attendance_data = models.Attendance.objects.filter(date=date, cl=cl)
            student_data = models.StudentExtra.objects.filter(cl=cl)
            return render(request, 'school/teacher_view_attendance_page.html', {
                'cl': cl,
                'attendance_data': attendance_data,
                'student_data': student_data,
                'date': date
            })
    else:
        form = forms.AskDateForm()
    return render(request, 'school/teacher_view_attendance_ask_date.html', {'cl': cl, 'form': form})

# Teacher Notice
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_notice_view(request):
    if request.method == 'POST':
        form = forms.NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.by = request.user.first_name
            notice.save()
            return redirect('teacher-dashboard')
    else:
        form = forms.NoticeForm()
    return render(request, 'school/teacher_notice.html', {'form': form})

# Student Dashboard
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    student_data = models.StudentExtra.objects.get(user=request.user, status=True)
    notices = models.Notice.objects.all()
    context = {
        'roll': student_data.roll,
        'mobile': student_data.mobile,
        'fee': student_data.fee,
        'notice': notices
    }
    return render(request, 'school/student_dashboard.html', context)

def student_waiting_approval_view(request):
    return render(request, 'school/student_waiting_approval.html')

def teacher_waiting_approval_view(request):
    return render(request, 'school/teacher_waiting_approval.html')
# Student Attendance
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_attendance_view(request):
    student = models.StudentExtra.objects.get(user=request.user)
    if request.method == 'POST':
        form = forms.AskDateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            attendance = models.Attendance.objects.filter(
                date=date, 
                cl=student.cl, 
                roll=student.roll
            ).first()
            return render(request, 'school/student_view_attendance_page.html', {
                'attendance': attendance,
                'date': date
            })
    else:
        form = forms.AskDateForm()
    return render(request, 'school/student_view_attendance_ask_date.html', {'form': form})

# Static Pages
def aboutus_view(request):
    return render(request, 'school/aboutus.html')

def contactus_view(request):
    if request.method == 'POST':
        form = forms.ContactusForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['Name']
            email = form.cleaned_data['Email']
            message = form.cleaned_data['Message']
            
            subject = f"Contact Form: {name}"
            body = f"From: {name} <{email}>\n\n{message}"
            
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_RECEIVING_USER],
                fail_silently=False
            )
            return render(request, 'school/contactussuccess.html')
    else:
        form = forms.ContactusForm()
    return render(request, 'school/contactus.html', {'form': form})

# views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout_view(request):
    logout(request)
    return redirect('home')  # or any other page
