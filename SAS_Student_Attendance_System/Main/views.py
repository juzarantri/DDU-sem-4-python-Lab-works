from os import error, name
from django.contrib.auth import login
from django.http import response
from django.http import HttpResponse
from django.shortcuts import redirect, render
from xlwt.Formatting import Font
from .models import Student,Teacher
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth.decorators import login_required
from datetime import date,datetime
import xlwt

# home page
def home(request):
    count = Student.objects.count()
    return render(request,'home.html',{
        'count':count
    })

# student registration page
@csrf_exempt
def registration_view(request):
    if request.method == 'POST':
        if request.POST['pass1'] == request.POST['pass2']:
                phone_no = request.POST['phone_no']
                parent_phone_no = request.POST['parent_phone_no']
                student_id = request.POST['student_id']
                roll_no = request.POST['roll_no']
                branch = request.POST['branch']
                email = request.POST['email']
                error = []
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM auth_user")
                for temp in cursor.fetchall():
                    if temp[4] == request.POST['uname']:
                        error.append("Username has already been taken")
                    if temp[7] == email:
                        error.append("Email has already been taken")
                if phone_no == parent_phone_no:
                    error.append("Your's and Parent's phone number cannot be same")
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM main_student")
                for temp in cursor.fetchall():
                    if temp[3] == phone_no:
                        error.append("Phone number must be unique")
                        break
                    if temp[4] == parent_phone_no:
                        error.append("Phone number must be unique")
                        break
                    if temp[6] == student_id:
                        error.append("Student id must be unique")
                        break
                    if temp[7] == roll_no and temp[5] == branch:
                        error.append("Roll NO. must be unique")
                        break
                if error:   
                    return render(request,'registration/signup.html',{
                    'error': error
                    })
                else:
                    username = request.POST['uname']
                    email = request.POST['email']
                    user = User.objects.create_user(username = username,password = request.POST['pass1'],email = email)
                    fullname = request.POST['fullname'] 
                    phone_no = request.POST['phone_no']
                    parent_phone_no = request.POST['parent_phone_no']
                    branch = request.POST['branch']
                    student_id = request.POST['student_id']
                    roll_no = request.POST['roll_no']
                    sem = request.POST['sem']
                    newStudent = Student(username = username,
                                            fullname = fullname,
                                            phone_no = phone_no,
                                            parents_phone_no = parent_phone_no,
                                            branch = branch,
                                            semester = "sem"+sem,
                                            student_id = student_id,
                                            roll_no = roll_no,
                                            user = user)
                    newStudent.save()
                    login(request,user)
                    return redirect('home')
        else:
            return render(request,'registration/signup.html',{
            'error': "Password Don't Match"
            })
    else:
        return render(request,'registration/signup.html')

# teacher registration page
def teacher_registration_view(request):
    if request.method == 'POST':
        if request.POST['pass1'] == request.POST['pass2']:
            try:
                User.objects.get(username=request.POST['uname'])
                return render(request,'registration/teacher_signup.html',{
                'error': "Username has already been taken"
                })
            except User.DoesNotExist:
                username = request.POST['uname']
                email = request.POST['email']
                user = User.objects.create_user(username = username,password = request.POST['pass1'],email = email,is_staff = True)
                
                fullname = request.POST['fullname'] 
                phone_no = request.POST['phone_no']
                newTeacher = Teacher(username = username,
                                          fullname = fullname,
                                          phone_no = phone_no,
                                          user = user)
                newTeacher.save()
                login(request,user)
                return redirect('/?id=1')
        else:
            return render(request,'registration/teacher_signup.html',{
            'error': "Password Don't Match"
            })
    else:
        return render(request,'registration/teacher_signup.html')

# Attendance start stop page
@login_required(login_url='')
def start_stop(request):
    return render(request,'attendance/start_stop.html')

# # starting attendance
@login_required(login_url='')
def startAttendance(request):
    if request.method == 'POST':
        branch = request.POST['branch']
        semester = request.POST['sem']
        subject = request.POST['subject']
        teacher = request.POST['teacher']
        tblname = branch+"_"+semester+"_"+subject
        error = []
        if branch == '':
            error.append("Branch must not be empty")
        if semester == "Select the semester":
            error.append("Please choose valid semester")
        if subject == '':
            error.append("Subject must not be empty")
        if error:
            return render(request,'attendance/start_stop.html',{
            'error': error
            })
        else:
            cursor = connection.cursor()
            on_going_attendance = []
            cursor.execute("CREATE TABLE IF NOT EXISTS attendance_start_stop (branch VARCHAR(50), semester VARCHAR(50), subject VARCHAR(50), status INT, tableName VARCHAR(50), faculty VARCHAR(50), FOREIGN KEY (faculty) REFERENCES main_teacher(username));")
            cursor.execute("SELECT * FROM attendance_start_stop WHERE tableName = '"+tblname+"' AND faculty = '"+teacher+"';")
            if cursor.fetchall():
                cursor.execute("CREATE TABLE IF NOT EXISTS "+tblname+" (name VARCHAR(50), student_id VARCHAR(50), roll_no VARCHAR(50), present INT, date DATE, time TIME, FOREIGN KEY (student_id) REFERENCES main_student(student_id),FOREIGN KEY (roll_no) REFERENCES main_student(roll_no));")
                today = date.today()
                d = today.strftime("%Y-%m-%d")
                cursor.execute("SELECT * FROM "+tblname+" WHERE date = '"+d+"';")
                if cursor.fetchall():
                    pass
                else:
                    cursor.execute("SELECT * FROM main_student WHERE branch = '"+branch+"' AND semester = '"+semester+"';")
                    data = cursor.fetchall()
                    for d in data:
                        sql = "INSERT INTO "+tblname+" VALUES(%s,%s,%s,%s,%s,%s);"
                        val = (d[2],d[1],d[7],0,date.today(),datetime.now())
                        cursor.execute(sql,val)
                sql = "UPDATE attendance_start_stop SET status = 1 WHERE tableName = '"+tblname+"';"
                cursor.execute(sql)
                cursor.execute("SELECT tableName FROM attendance_start_stop WHERE faculty = '"+teacher+"' AND status = 1 ;")
                tableNames = cursor.fetchall()
                for table in tableNames:
                    temp = table
                    s = ""
                    for t in range(len(temp)):
                        if table[t] == '(' or table[t] == ')' or table[t] == ',' or table[t] == "'" :
                            pass
                        else:
                            s += table[t]
                    table = s
                    on_going_attendance.append(table)
            else:
                cursor.execute("CREATE TABLE IF NOT EXISTS "+tblname+" (name VARCHAR(50), student_id VARCHAR(50), roll_no VARCHAR(50), present INT, date DATE, time TIME);")
                today = date.today()
                d = today.strftime("%Y-%m-%d")
                cursor.execute("SELECT * FROM "+tblname+" WHERE date = '"+d+"';")
                if cursor.fetchall():
                    pass
                else:
                    cursor.execute("SELECT * FROM main_student WHERE branch = '"+branch+"' AND semester = '"+semester+"';")
                    data = cursor.fetchall()
                    for d in data:
                        sql = "INSERT INTO "+tblname+" VALUES(%s,%s,%s,%s,%s,%s);"
                        val = (d[2],d[1],d[7],0,date.today(),datetime.now())
                        cursor.execute(sql,val)
                sql = "INSERT INTO attendance_start_stop VALUES(%s,%s,%s,%s,%s,%s);"
                val = (branch,semester,subject,1,tblname,teacher)
                cursor.execute(sql,val)
                cursor.execute("SELECT tableName FROM attendance_start_stop WHERE faculty = '"+teacher+"' AND status = 1 ;")
                tableNames = cursor.fetchall()
                for table in tableNames:
                    temp = table
                    s = ""
                    for t in range(len(temp)):
                        if table[t] == '(' or table[t] == ')' or table[t] == ',' or table[t] == "'" :
                            pass
                        else:
                            s += table[t]
                    table = s
                    on_going_attendance.append(table)
            return render(request,'attendance/start_stop.html',{
                'message':"Attendance for "+branch+" "+semester+" "+subject+" has been started",
                'on_going_attendance':on_going_attendance
            })
    else:
        return render(request,'attendance/start_stop.html')

# stopping attendance
@login_required(login_url='')
def stopAttendance(request,table,teacher):
        maintable = table
        teacher = teacher
        on_going_attendance = []
        cursor = connection.cursor()
        sql = "UPDATE attendance_start_stop SET status = 0 WHERE tableName = '"+table+"' AND faculty = '"+teacher+"';"       
        cursor.execute(sql)
        cursor.execute("SELECT tableName FROM attendance_start_stop WHERE faculty = '"+teacher+"' AND status = 1 ;")
        tableNames = cursor.fetchall()
        for table in tableNames:
            temp = table
            s = ""
            for t in range(len(temp)):
                if table[t] == '(' or table[t] == ')' or table[t] == ',' or table[t] == "'" :
                    pass
                else:
                    s += table[t]
                table = s
                on_going_attendance.append(table)
        return render(request,'attendance/start_stop.html',{
                'message':"Attendance for "+maintable+" has been stopped",
                'on_going_attendance':on_going_attendance
        })

#refreshing table
@login_required(login_url='')
def refreshAttendanceTable(request,teacher):
    teacher = teacher
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS attendance_start_stop (branch VARCHAR(50), semester VARCHAR(50), subject VARCHAR(50), status INT, tableName VARCHAR(50), faculty VARCHAR(50), FOREIGN KEY (faculty) REFERENCES main_teacher(username));")
    cursor.execute("SELECT tableName FROM attendance_start_stop WHERE faculty = '"+teacher+"' AND status=1 ;")
    tableNames = cursor.fetchall()
    on_going_attendance = []
    for table in tableNames:
        temp = table
        s = ""
        for t in range(len(temp)):
            if table[t] == '(' or table[t] == ')' or table[t] == ',' or table[t] == "'" :
                pass
            else:
                s += table[t]
        table = s
        on_going_attendance.append(table)
    if tableNames:
        return render(request,'attendance/start_stop.html',{
        'on_going_attendance': on_going_attendance,
    })
    else:
        error = []
        error.append("You haven't started any attendance yet!!")
        return render(request,'attendance/start_stop.html',{
            'error': error,
        })

# Make Attendance page
@login_required(login_url='')
def makeAttendance(request):
    return render(request,'attendance/make_attendance.html')

@login_required(login_url='')
def refreshStudentAttendanceTable(request,username):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM main_student WHERE username = '"+username+"';")
    temp = cursor.fetchall()
    for t in temp:
        branch = t[5]
        sem = t[10]
    cursor.execute("SELECT tableName FROM attendance_start_stop WHERE semester = '"+sem+"' AND branch = '"+branch+"' AND status = '1';")
    tableNames = cursor.fetchall()
    on_going_attendance = []
    for table in tableNames:
        temp = table
        s = ""
        for t in range(len(temp)):
            if table[t] == '(' or table[t] == ')' or table[t] == ',' or table[t] == "'" :
                pass
            else:
                s += table[t]
        table = s
        on_going_attendance.append(table)
    if tableNames:
        return render(request,'attendance/make_attendance.html',{
        'on_going_attendance': on_going_attendance,
    })
    else:
        error = []
        error.append("OOPS! seems no attandance has been started")
        return render(request,'attendance/make_attendance.html',{
        'error': error,
    })

# student clicks present
@login_required(login_url='')
def clickedPresent(request,table,student):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM "+table+" WHERE student_id = '"+student+"' AND date = '"+str(date.today())+"' AND present = 1;" )
    if cursor.fetchall():
        error = []
        error.append("You are alerady present")
        return render(request,'attendance/make_attendance.html',{'error':error})
    else:
        today = date.today()
        d = today.strftime("%Y-%m-%d")
        cursor.execute("UPDATE "+table+" SET present = 1, time = '"+str(datetime.now())+"' WHERE student_id = '"+student+"' AND date = '"+d+"';")
        return render(request,'attendance/make_attendance.html',{'message':"Your Attendance have been successfull recognized for "+table})

# view attendance
@login_required(login_url='')
def viewAttendance(request):
    return render(request,"attendance/view_attendance.html")

# get attendance
@login_required(login_url='')
def getAttendance(request,username):
    if request.method == "POST":
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM main_student WHERE username = '"+username+"';")
        temp = cursor.fetchall()
        attendanceData = []
        for t in temp:
            branch = t[5]
            sem = t[10]
        tblname = branch+"_"+sem+"_"+request.POST['subject']
        cursor.execute("SELECT tableName FROM attendance_start_stop WHERE tableName = '"+tblname+"';")
        if cursor.fetchall():
            cursor.execute("SELECT present,date,time FROM "+tblname+" WHERE student_id = '"+username+"';")
            for temp in cursor.fetchall():
                t = {"present":temp[0],"date":temp[1],"time":temp[2]}
                attendanceData.append(t) 
            return render(request,"attendance/view_attendance.html",{
                'attendanceData':attendanceData,
                'message':"Your attendance in "+request.POST['subject']+" is as follows:"
            })
        else:
            error = []
            error.append("No details found for "+request.POST['subject'])
            return render(request,"attendance/view_attendance.html",{
                'error':error
            })
    else:
        return render(request,"attendance/view_attendance.html")

# rendering generate muster view
def generateMusterView(request):
    return render(request,"attendance/generate_muster.html")

# exporting attendance data to muster
def generateMuster(request):
    if request.method == "POST":
        response = HttpResponse(content_type = 'application/ms-excel')
        response['content-Disposition'] = 'attachment; filename=Attendance'+\
            str(datetime.now())+'.xls'

        branch = request.POST['branch']
        sem = request.POST['sem']
        subject = request.POST['subject']
        startDate = request.POST['start_date']
        endDate = request.POST['end_date']
        tblname = branch+"_"+sem+"_"+subject

        cursor = connection.cursor()
        # first getting all tablename and checking if there is attendance data or not
        cursor.execute("SELECT tableName FROM attendance_start_stop WHERE faculty = '"+request.user.username+"'")
        flag = 0
        for temp in cursor.fetchall():
            if temp[0].lower() == tblname.lower():
                flag = 1
        if flag == 1:
            # adding heading to excel file
            style = xlwt.XFStyle()
            style.font.bold = True
            style.alignment.wrap = 1 # Set wrap
            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet('My Worksheet')
            worksheet.write_merge(0, 0, 0, 20, 'DHARMSINH DESAI UNIVERSITY, NADIAD', xlwt.easyxf('align: horz center, vert center;pattern: pattern solid, fore_colour white;font: colour black, bold True, height 420;'))
            worksheet.write_merge(1, 1, 0, 20, 'Attendance report for '+branch+' '+sem+' '+subject+' ', xlwt.easyxf('align: horz center, vert center;pattern: pattern solid, fore_colour white;font: colour black, bold True, height 320;'))
            worksheet.write_merge(2, 2, 0, 20, 'From Date:'+startDate+'                       To Date:'+endDate+'', xlwt.easyxf('align: horz center, vert center;font: colour red, bold True, height 220;'))
            first_col = worksheet.col(1)
            first_col.width = 420*20
            worksheet.write(3, 0, "Roll NO.", xlwt.easyxf('align: horz center, vert center;pattern: pattern solid, fore_colour white;font: colour black, bold True;'))
            worksheet.write(3, 1, "Sutudent name", xlwt.easyxf('align: horz center, vert center;pattern: pattern solid, fore_colour white;font: colour black, bold True;'))

            # setting roll no and name of student in excel
            row = 5
            cursor.execute("SELECT name,roll_no FROM "+tblname+" WHERE date BETWEEN '"+startDate+"' AND '"+endDate+"' GROUP BY roll_no ORDER BY roll_no")
            for temp in cursor.fetchall():
                worksheet.write(row, 0, temp[1])
                worksheet.write(row, 1, temp[0])
                row += 1
            # setting date row
            cursor.execute("SELECT date FROM "+tblname+" WHERE date BETWEEN '"+startDate+"' AND '"+endDate+"' GROUP BY date")
            col = 2
            month_col = 2
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            initial_month = -1
            prev_month = -1
            last_month = -1
            count = 2
            for temp in cursor.fetchall():
                initial_month = int(str(temp[0])[5:7]) - 1
                last_month = initial_month
                if initial_month == prev_month:
                    pass
                else:
                    if count > month_col:
                        worksheet.write_merge(3,3,month_col,count - 1,months[prev_month],xlwt.easyxf('align: horz center, vert center;pattern: pattern solid, fore_colour white;font: colour black, bold True;'))
                        month_col = count
                    prev_month = initial_month
                temp_col = worksheet.col(col)
                temp_col.width = 25 * 25
                worksheet.write(4, col, str(temp[0])[8:10])
                count += 1
                col += 1
            if last_month != -1:
                worksheet.write_merge(3,3,month_col,count - 1,months[last_month],xlwt.easyxf('align: horz center, vert center;pattern: pattern solid, fore_colour white;font: colour black, bold True;'))
            # getting data from database between start and end date
            cursor.execute("SELECT * FROM "+tblname+" WHERE date BETWEEN '"+startDate+"' AND '"+endDate+"' ORDER BY roll_no, date")
            row = 4
            col = 2
            prev_roll_no = ''
            for temp in cursor.fetchall():
                initial_roll_no = str(temp[2])
                if initial_roll_no == prev_roll_no:
                    col += 1
                else:
                    prev_roll_no = initial_roll_no
                    row += 1
                    col = 2
                if temp[3] == 1:
                    worksheet.write(row, col, "P",xlwt.easyxf('font: colour green;'))
                else:
                    worksheet.write(row, col, "A",xlwt.easyxf('font: colour red;'))
            workbook.save(response)
            return response
        else:
            error = []
            error.append("OPPS!! no data found")
            return render(request,"attendance/generate_muster.html",{'error':error}) 
    else:
        return render(request,"attendance/generate_muster.html")

    
    