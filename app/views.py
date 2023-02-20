from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import logout as django_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import user_info,contact_us
from django.core.mail import EmailMessage
import csv
from app.encryption_util import *

from django.shortcuts import render, get_object_or_404, reverse
import re
import pandas as pd

 
# Create your views here.


# Login Page
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("home")

    return render(request,'index.html')


# Register Page
def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("home")
    return render(request,"register.html")


# Register User
def register_user(request):
    if request.method == "POST":
        fn = request.POST["fname"]
        ln = request.POST["lname"]
        wp = request.POST["wplace"]
        st = request.POST["state"]
        mn = request.POST["mobile"]
        em = request.POST["email"]
        pd = request.POST["password"]
        
        usr = User.objects.create_user(em,em,pd)
        usr.first_name = fn
        usr.last_name = ln
        usr.is_active = False
        usr.save()
        
        res = user_info(user=usr,wplace=wp,state=st,mobile=mn)
        res.save()
        
        user = User.objects.get(username=em)
        uid = encrypt(user.id)
        
        link = "http://127.0.0.1:8000/user/"+str(uid)
        sub = "Account Request"
        msg = "Receiving a Account Request from "+fn+" check the account by clicking the link:\n"+link
        to = "bgmilinked@gmail.com"
        try:
            mail = EmailMessage(sub,msg,to=[to])
            mail.send()
            print("sent")
        except:
            print("not sent")
        return HttpResponseRedirect("register_msg")
    return render(request,"register.html")


# Register Message
def register_msg(request):
    pass
    return render(request,"register_msg.html")


# Accounts Request
def requests(request):
    if request.user.is_authenticated:
        context = {}
        user =  User.objects.get(id=request.user.id)
        context["data"] = user
        c=0
        if user.is_staff:
            all_users_ency = User.objects.values('id','first_name','last_name','is_active','date_joined').order_by("-date_joined")
            li = []
            for i in all_users_ency:
                i['encrypt_key']=encrypt(i['id'])
                i['id'] = i['id']
                li.append(i)
            context['users'] = li
            for i in all_users_ency:
                if i['is_active']==False:
                    c+=1
            context["count"] = c
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    return render(request,"requests.html",context)



# Users
def user(request,uid):
    if request.user.is_authenticated:
        if request.method == "GET":
            context = {}
            user =  User.objects.get(id=request.user.id)
            context["data"] = user
            if user.is_staff:
                uid = decrypt(uid)
                # uid = request.GET['uid']
                check =  User.objects.filter(id=uid)
                if len(check)>0:
                    ruser =  User.objects.get(id=uid)
                    ruser_details = user_info.objects.get(user__id=uid)
                    print(ruser_details)
                    context["ruser"] = ruser
                    context["ruser_detail"] = ruser_details
                    context["encrypt_key"] = encrypt(uid)
                else:
                    return HttpResponseRedirect("/requests")
            else:
                return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    return render(request,"user.html",context)


# Accept User Request
def accepted(request,uid):
    if request.user.is_authenticated:
        if request.method == "GET":
            context = {}
            user =  User.objects.get(id=request.user.id)
            context["data"] = user
            if user.is_staff:
                uid = decrypt(uid)
                # uid = request.GET['uid']
                check =  User.objects.filter(id=uid)
                if len(check)>0:
                    ruser = User.objects.get(id=uid)
                    ruser.is_active = True
                    ruser.save()
                    link = "http://127.0.0.1:8000/"
                    sub = "Your account has been Activated"
                    msg = "Greetings,\nYour account has been Activated, now you can able to access our website by using this link:\n"+link
                    to = ruser.email
                    try:
                        mail = EmailMessage(sub,msg,to=[to])
                        mail.send()
                        print("sent")
                    except:
                        print("not sent")
                    return HttpResponseRedirect("/requests")
                else:
                    return HttpResponseRedirect("/requests")
            else:
                return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    return render(request,"user.html",context)



# Delete User
def delete_user(request,uid):
    if request.user.is_authenticated:
        if request.method == "GET":
            context = {}
            user =  User.objects.get(id=request.user.id)
            context["data"] = user
            if user.is_staff:
                uid = decrypt(uid)
                # uid = request.GET['uid']
                check =  User.objects.filter(id=uid)
                if len(check)>0:
                    ruser =  User.objects.get(id=uid)
                    ruser.delete()
                    return HttpResponseRedirect("/requests")
                else:
                    return HttpResponseRedirect("/requests")
            else:
                return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    return render(request,"user.html",context)



# Check User Exists or Not
def check_user(request):
    if request.method == "GET":
        un = request.GET["usern"]
        res = User.objects.filter(username=un)
        if len(res)==1:
            return HttpResponse("exists")
        else:
            return HttpResponse("not exists") 
        
        
 
# Forgot password
def forgot_password(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/home")
    else:
        context= {}
        if request.method == "POST":
            email = request.POST["email"]
            npassword = request.POST["newpassword"]
            user = User.objects.get(username=email)
            if user:
                ruser = user_info.objects.get(user__id=user.id)
                ruser.otp = ""
                user.set_password(npassword)
                user.save()
                ruser.save()
                context["message"] = "Password Reset Successfully"
            else:
                context["message"] = "User Not Found"
    return render(request,"forgot_password.html",context)


# Send OTP for Change Password
import random
def send_otp(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/home")
    else:
        context = {}
        if request.method == "GET":
            email = request.GET['email']
            try:
                user = User.objects.get(username=email)
                if user.is_active:
                    otp = random.randint(1000,9999)
                    ruser = user_info.objects.get(user__id=user.id)
                    ruser.otp = otp
                    ruser.save()
                    try:
                        sub = "Reset Your Password"
                        msg = "Dear {}\n{} is your One Time Password (OTP)\nDo not share it with others\n\n\nThanks&Regards\nTicket Extracter".format(user.first_name,otp)
                        mail = EmailMessage(sub,msg,to=[email])
                        mail.send()
                        print("sent")
                        return JsonResponse({"result":"success","email":email})
                    except:
                        return JsonResponse({"result":"error","email":email})
                else:
                    return JsonResponse({"result":"notactive"})
            except:
                return JsonResponse({"result":"failed"})
                
        else:
            return HttpResponseRedirect("/") 
    return render(request,"forgot_password.html")


# Check OTP for Change Password
def check_otp(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/home")
    else:
        if request.method == "GET":
            uotp = request.GET['otp']
            email = request.GET['email']
            user = User.objects.get(username=email)
            ruser = user_info.objects.get(user__id=user.id)
            if uotp == ruser.otp:
                return JsonResponse({"result":"matched"})
            else:
                return JsonResponse({"result":"notmatched"})
        else:
            return HttpResponseRedirect("/") 
    return render(request,"forgot_password.html")

        
           

# User Login
def user_login(request):
    if request.method == "POST":
        uname = request.POST["email"]
        upass = request.POST["password"]

        user = authenticate(username=uname,password=upass)
        if user:
            login(request,user)
            if user.is_superuser:
                return HttpResponseRedirect("/requests")
            elif user.is_staff:
                return HttpResponseRedirect("home")
                # return HttpResponseRedirect("/admin")
            elif user.is_active:
                return HttpResponseRedirect("home")
                # return HttpResponseRedirect("/admin")
        else:
            return render(request,"index.html",{"status":"invalid username or password"})
    return HttpResponseRedirect("/login/")





# contact us
import time
def contact(request):
    if request.user.is_authenticated:
        context = {}
        try:    
            user =  User.objects.get(id=request.user.id)
            context["data"] = user
            if request.method == "POST":
                subject = request.POST["subject"]
                message = request.POST["message"]
                row = contact_us()
                row.email = user.email
                row.subject = subject
                row.message = message
                row.save()
                context["message"] = "submited"
            else:
                return render(request,"contact.html",context)
        except:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    return render(request,"contact.html",context)



def messages(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            context = {}
            context["data"] = request.user
            rows = contact_us.objects.all().order_by("-added_on")
            context["rows"] = rows
            context["count"] = len(rows)
            new = 0
            checked = 0
            for i in rows:
                if i.status == False:
                    new+=1
                else:
                    checked+=1
            context["new"]=new
            context["checked"]=checked
            try:
                uid = request.GET["uid"]
                action = request.GET["action"]
                row = contact_us.objects.get(id=uid)
                print(row)
                if action=="check":
                    row.status = True
                    row.save()
                    return HttpResponseRedirect("messages")
                elif action=="delete":
                    row.delete()
                    return HttpResponseRedirect("messages")
                else:
                    return render(request,"messages.html",context)
            except:
                return render(request,"messages.html",context)
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    return render(request,"messages.html",context)


# User Logout
# @login_required
def logout(request):
    if request.user.is_authenticated:
        django_logout(request)
    return HttpResponseRedirect("/")
    
    
# Home Page
global list_of_details
list_of_details = []
def home(request):
    if request.user.is_authenticated:
        context = {}
        user =  User.objects.get(id=request.user.id)
        context["data"] = user
        list_of_details.clear()
        return render(request,"home.html",context)
    else:
        return HttpResponseRedirect("/")
    return render(request,"home.html",context)


@csrf_exempt
def upload_file(request):
    pass
    return HttpResponse("called")


# Extract Files
from django.http import JsonResponse
import pypdfium2 as pdfium
import re
def extract_files(request):  
    if request.user.is_authenticated:
        if "file" in request.FILES:
            context = {}
            user =  User.objects.get(id=request.user.id)
            context["data"] = user
            pdf_files = 0
            not_pdf = 0
            list_of = []
            unknown_files = []
            global all_files
            files = request.FILES.getlist('file')
            all_files = files
            for j in files:
                fail = 1
                try:
                    pdfpath=pdfium.PdfDocument(j)
                    n_pages= len(pdfpath)
                    text=' '
                    for i in range(n_pages):
                        textpage= pdfpath[i].get_textpage()
                        text= text+textpage.get_text_range()
                    list_of_text = text.split("\r\n")
                    jdate,time_dep,time_arr,pnr,tnc,train_number,train_class,train_name,booking_details,booking_date,boarding,departure,refund_amount,ticket_fare,refund_fare='\0','\0','\0','\0','\0','\0','\0','\0','\0','\0','\0','\0','\0','\0','\0'
                    
                    # Journey Date
                    try:
                        strt_date = re.search(r'\d{2}:\d{2}\s\d{2}-\w*-\d{4}',text)
                        jdate = re.search(r'\d{2}-\w*-\d{4}',strt_date.group(0))
                        jdate = jdate.group(0)
                        # print("journey_date :",jdate)
                    except:
                        jdate=text[text.find('Start Date*')+len('Start Date*')+1: text.find("Departure*")]
                        # print("journey_date :",jdate)

                    # Departure Time
                    time_dep=text[text.find('Departure*')+len('Departure*')+1: text.find("Arrival*")].split(' ')[0]
                    # print("time_dep: ",time_dep)
                    date=re.search(r'\d{2}-\w{3,}-\d{4}',text)
                    
                    # Arrival Time
                    time_arr=text[text.find('Arrival*')+len('Arrival*')+1:text.find(r'\d{2}-\w{3,}-\d{4}')].split(' ')[0]
                    time_arrival = time_arr.split("\r\n")[0]
                    # print("time_arr: ",time_arrival)
                    
                    # Total Fare
                    total_fare=[]
                    start = list_of_text.index("Payment Details")
                    end = list_of_text.index("PG Charges as applicable (Additional)")
                    for st in list_of_text[start:end]:
                        fare = re.search(r'[\d,,]*\.\d*',st)
                        if fare != None:
                            total_fare.append(fare.group(0))
                    refund_fare = total_fare[0]
                    total_fare = total_fare[-1]
                    ticket_fare = total_fare
                    
                    # PNR Number
                    pnr=text[text.find('PNR Train No./Name Class')+len("PNR Train No./Name Class")+1 : text.find('Quota Distance Booking Date')].split(' ')[0]
                    pnr = pnr.strip()
                    # print("pnr_number :",pnr)
                    
                    
                    # Train Number & Train Name & Class
                    # tnc=text[text.find('PNR Train No./Name Class')+len("PNR Train No./Name Class")+1 : text.find('Quota Distance Booking Date')]
                    tnc = re.search(r'\d{5}\s?\/\s?[A-Z,\s]*\s?\([\d,A-Z]*\)',text)
                    tnc_list = []
                    tnc_list = tnc.group(0).split("/")
                    
                    # Train Number
                    # train_number = re.search(r'\d{5}',tnc)
                    # train_number = re.search(r'\d{5}',tnc.group(0))
                    # print("train_number :",train_number.group(0))
                    train_number = tnc_list[0]
                    # print("train_number :",train_number)
                    
                    # Train Class
                    # train_class = re.search(r'[A-Z]*\s[A-Z]*\s[A-Z]*\s\([\d,A-Z]*\)',tnc)
                    train_class = tnc_list[1]
                    train_class = train_class.replace("\r\n"," ")
                    # print("train_class :",train_class)
                    
                    # Train Name
                    # train_name = tnc_list[1][0:-(len(train_class.group(0)))]
                    # print("train_name :",train_name)
                    train_name = tnc_list[1]
                    train_name = train_name.replace("\r\n"," ")
                    # print("train_name :",train_name)
                    
                    
                    # Booking Date
                    # s=text[text.find('Booking Date')+len("Booking Date") :text.find("Passenger Details")]
                    booking_details = re.search(r'\d{2}-[A-Z,a-z,\d]*-\d{4}\s\d{2}:\d{2}:\d{2}\s[HRS,Hrs,hrs]*',text)
                    bookingdate = re.search(r'\d{2}-\w*-\d{4}',booking_details.group(0))
                    booking_date = bookingdate.group(0)
                    # print("booking_date :",booking_date)
                    

                    # From & To
                    start_list = []
                    for start in list_of_text:
                        start_exp = re.search(r'[A-Z,\s]*\s\([A-Z]*\)\s[A-Z,\s]*\s\([A-Z]*\)',start)
                        if start_exp != None:
                            start_list = start.split(')')

                    # From
                    boarding = start_list[0]+")"
                    # print("boarding :",boarding)
                    
                    # To
                    departure = start_list[-2]+")"
                    # print("departure :",departure)
                    
                    #Passenger Details
                    passengers = []
                    names = ""
                    # booking_status = ""
                    current_status = ""
                    coach_no = ""
                    seat_no = ""
                    berth = ""
                    no_of_names = 0
                    for line in list_of_text:
                        passenger = re.search(r'\d?\.?\s?[A-Z,\s]+\s\d{2}\s[M,MALE,Male,male,F,FEMALE,Female,female]*',line)
                        if passenger !=None:
                            passengers.append(line)
                            no_of_names+=1
                    for details in passengers:
                        start = re.search(r'\d{2}',details).group(0)
                        end = re.search(r'[A-Z]*\s?/',details).group(0)
                        start_ind = details.find(start)
                        end_ind = details.find(end)
                        gender=details[start_ind+2:end_ind]
                        details_list=details.split(gender)
                        name = re.search(r'\d\.[A-Z,\s]*',details)
                        names+=name.group(0)+"; "
                        status = (details_list[-1].strip()).split(" ")
                        status_length=0
                        for text in status:
                            status_length+=1
                        if status_length == 5:
                            concat = status[-3]+status[-2]+" "+status[-1]
                        elif status_length == 4:
                            if status[-3]=="CNF" or status[-3]=="Cnf" or status[-3]=="cnf" or status[-3]=="CONFIRMED" or status[-3]=="Confirmed" or status[-3]=="confirmed":
                                concat = status[-3]+status[-2]+" "+status[-1]
                            else:
                                concat = status[-2]+" "+status[-1]
                        elif status_length == 3:
                            if status[-1]=="CAN" or status[-1]=="Can" or status[-1]=="can" or status[-1]=="CANCELLED" or status[-1]=="Cancelled" or status[-1]=="cancelled":
                                concat = status[-1]
                            else:
                                concat = status[-2]+" "+status[-1]
                        else:
                            concat = status[-1]
                            
                        # Current Status
                        current_details = concat.split("/") 
                        current_length = len(current_details)
                        if current_length==4:
                            current_status += current_details[0]+", "
                            coach_no += current_details[1]+", "
                            seat_no += current_details[2]+", "
                            berth += current_details[3]+", "
                        
                        elif current_length==2:
                            current_status += current_details[0]+", "
                            seat_no += current_details[1]+", "
                        
                        elif current_length==1:
                            if current_details[0]=="CAN" or current_details[0]=="Can" or current_details[0]=="can" or current_details[0]=="CANCELLED" or current_details[0]=="Cancelled" or current_details[0]=="cancelled":
                                refund_amount = total_fare
                                ticket_fare = refund_fare
                            else:
                                refund_amount = "-"
                                ticket_fare = total_fare
                            current_status += current_details[0]+", "  
                    # print("Names :\n",names.encode("ascii","ignore").decode())
                    # print("current_status :\n",len(current_status),current_status)
                    # print("coach_no :\n",coach_no)
                    # print("seat_no :\n",seat_no)
                    # print("berth :\n",berth)
                    all_details = (jdate,boarding,departure,train_name,train_number,time_dep,time_arrival,pnr,booking_date,names.encode("ascii","ignore").decode(),no_of_names,current_status.encode("ascii","ignore").decode(),coach_no,seat_no,berth,ticket_fare,refund_amount)
                    # all_details = [jdate,boarding,departure,train_name,train_number,time_dep,time_arrival,pnr,booking_date,names.encode("ascii","ignore").decode(),no_of_names,current_status.encode("ascii","ignore").decode(),coach_no,seat_no,berth,ticket_fare,refund_amount]
                    list_of.append(all_details)
                    fail = 0
                    pdf_files+=1
                except:
                    if fail == 1:
                        file_type = (str(j)[-1:-5:-1])
                        if file_type[::-1] == ".pdf":
                            unknown_files.append(j)
                            not_pdf+=1
                            fail = 0
            pnr_position = 7
            no_of_names_position = 10
            status_position = 11
            total_fare_position = 15
            # Remove Duplicates
            import itertools
            global list_of_details
            list_of_details = []
            list_of_tuples = list(set([tuplee for tuplee in list_of])) # Remove duplecates for list of tuples
            # list_of_details = list(list_of_details for list_of_details,_ in itertools.groupby(list_of_details)) # Remove duplecates for list of lists
            
            list_of_tuples_length = len(list_of_tuples)
            
            for ijk in range(list_of_tuples_length):
                list_of_tuple = list_of_tuples[ijk]
                conv_list = list(list_of_tuple)
                list_of_details.append(conv_list)
            
            
            # Remove confirmed tickets incase of cancelled
            for tuple1 in list_of_details:
                for tuple2 in list_of_details:
                    if tuple1 == tuple2:
                        pass
                    else:
                        if tuple1[pnr_position] == tuple2[pnr_position] and tuple1[no_of_names_position] == tuple2[no_of_names_position]:
                            if ("CAN, " in tuple1[status_position]) or "Can, " in (tuple1[status_position]) or ("can, " in tuple1[status_position]) or ("CANCELLED, " in tuple1[status_position]) or ("Cancelled, " in tuple1[status_position]) or ("cancelled, " in tuple1[status_position]):
                                print(tuple1[total_fare_position] , tuple2[total_fare_position])
                                tuple1[total_fare_position] = tuple2[total_fare_position]
                                print(tuple1[pnr_position]," :",tuple1[total_fare_position])
                                list_of_details.remove(tuple2)
                                
                            elif ("CAN, " in tuple2[status_position]) or ("Can, " in tuple2[status_position]) or ("can, " in tuple2[status_position]) or ("CANCELLED, " in tuple2[status_position]) or ("Cancelled, " in tuple2[status_position]) or ("cancelled, " in tuple2[status_position]):
                                print(tuple2[total_fare_position] , tuple1[total_fare_position])
                                tuple2[total_fare_position] = tuple1[total_fare_position]
                                print(tuple2[pnr_position]," :",tuple2[total_fare_position])
                                list_of_details.remove(tuple1)
                        elif tuple1[pnr_position] == tuple2[pnr_position] and tuple1[no_of_names_position] != tuple2[no_of_names_position]:
                            if ("CAN, " in tuple1[status_position]) or "Can, " in (tuple1[status_position]) or ("can, " in tuple1[status_position]) or ("CANCELLED, " in tuple1[status_position]) or ("Cancelled, " in tuple1[status_position]) or ("cancelled, " in tuple1[status_position]):
                                tuple1[total_fare_position] = tuple2[total_fare_position]
                                
                            elif ("CAN, " in tuple2[status_position]) or ("Can, " in tuple2[status_position]) or ("can, " in tuple2[status_position]) or ("CANCELLED, " in tuple2[status_position]) or ("Cancelled, " in tuple2[status_position]) or ("cancelled, " in tuple2[status_position]):
                                tuple2[total_fare_position] = tuple1[total_fare_position]
                            
                                
                            
            # Sorting the data based on pnr number
            list_of_details_length = len(list_of_details)
            for first_tuple in range(0,list_of_details_length):
                for second_tuple in range(0,list_of_details_length):
                    if (list_of_details[first_tuple][pnr_position] <= list_of_details[second_tuple][pnr_position]):
                        list_of_details[first_tuple],list_of_details[second_tuple] = list_of_details[second_tuple],list_of_details[first_tuple]
            
            # print(list_of_details)
            
            print("pdf = %d, unknown = %d" %(pdf_files,not_pdf))
            context["not_pdf"] = not_pdf
            context["unknown_files"] = unknown_files
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    
    return render(request,"download.html",context)
    
    
# def check(request):
#     return render(request,"download.html")

    
# Download CSV File
import os
def download(request):
    if request.user.is_authenticated:
        context = {}
        user =  User.objects.get(id=request.user.id)
        context["data"] = user
        if request.method == "POST":
            filename = request.POST["file_name"]
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="'+filename+'.csv"'
            writer = csv.writer(response,escapechar='\\')
            writer.writerow(['JOURNEY DATE','FROM','TO','TRAIN NAME','TRAIN NUMBER','TIME OF DEPARTURE','TIME OF ARRIVAL','PNR NUMBER','BOOKING DATE','PASSENGERS','NUMBER OF PASSENGERS','STATUS','COACH NUMBER','SEAT NUMBER','BERTH','TOTAL TICKET FAIR','REFUND AMOUNT'])
            for i in list_of_details:
                writer.writerow(i)
            return response
        return HttpResponseRedirect("/")    
    else:
        return HttpResponseRedirect("/")    
    return render (request,"download.html",context)
 