import json,jwt,datetime
import bcrypt
from django.http import JsonResponse
from django.shortcuts import render
from .serializer import UserSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .passwords import password_hash
 
from django.conf import settings
SECRET_KEY=settings.SECRET_KEY

# Create your views here.

def home_page(req):
    try:
        auth_token=req.headers.get('Authorization')
        auth_token=auth_token.split(' ')[1]

        user_info=jwt.decode(auth_token,SECRET_KEY,algorithms='HS256')
        print(user_info)
    except Exception as e:
        return JsonResponse({'error':'user verification failed'})

     
    # if req.session.get('location')=='India':
    # if req.COOKIES.get('is_logged_in'):
    return JsonResponse({'status':200,'message':"show india home page"})
    # else:
        # return JsonResponse({'status':200,'message':'show US homepage'})

@csrf_exempt
def register(req):
    print(req.body)
    data=json.loads(req.body)

    u1=UserSerializer(data=data)
    if u1.is_valid():
        print(u1.validated_data)
        # sent_password=u1.validated_data['password'].encode('utf-8')
        # salt=bcrypt.gensalt(rounds=12)
        # hashed_password=bcrypt.hashpw(sent_password,salt)
        hashed_password=password_hash(u1.validated_data['password'])
        u1.validated_data['password']=hashed_password



        u1.save()
       
        return JsonResponse({'status':'user created','data':u1.data})
    else:
        return JsonResponse(u1.errors)
    
@csrf_exempt
def login(req):
    # if 'is_logged_in' in req.COOKIES:
    #     message='you are already logged in '+req.COOKIES.get('username')
    #     return JsonResponse({'status':200,'message':message})

    # #sessions
    # username=req.session.get('username')
    # if req.session.get('username'):
    #     return JsonResponse({
    #         "status":"you already logged in"+ " "+username
    #     })


    data=json.loads(req.body)
    # User.objects.filter
    try:
        u1=User.objects.get(username=data['username'])
    except Exception as e:
        return JsonResponse({'error':"login failed...check username and password"})
    

    entered_password=data['password']
    database_password=u1.password

    if bcrypt.checkpw(entered_password.encode('utf-8'),database_password.encode('utf-8')):
           data={
               'username':u1.username,
               'location':'India',
               'iat':datetime.datetime.now(datetime.timezone.utc)
           }
           token=jwt.encode(data,SECRET_KEY,algorithm='HS256')

           response=JsonResponse({'status':200,'user_token':token})
           return response






           response=JsonResponse({'status':200})
           #sessions
        #    req.session['username']=u1.username
        #    req.session['location']='india'
        #    response.set_cookie(
        #        key='username',
        #        value=data['username'],
        #        max_age=3600,

        #    ) 
        #    response.set_cookie(
        #        key='is_logged_in',
        #        value='true',
        #        max_age=3600,
               
        #    ) 
        #    return response
    return JsonResponse({'status':'login failed'})

@csrf_exempt
def update(req):

    if not 'is_logged_in' in req.COOKIES:
        return JsonResponse({'error':'login first'})

    data=json.loads(req.body)

    try:
        u1=User.objects.get(username=data.get('username'))
    except Exception as e:
        return JsonResponse({'error':"user not found"})
    
    sent_password=data.get('password').encode('utf-8')
    salt=bcrypt.gensalt(rounds=12)
    hashed_password=bcrypt.hashpw(sent_password,salt)
    data['password']=hashed_password.decode('utf-8')


    u1=UserSerializer(u1,data=data,partial=True)
    if u1.is_valid():
        u1.save()
        return JsonResponse({'status':"password changed"})
    else:
        return JsonResponse(u1.errors)
    
    
# def set_cookie(req):
#     response=JsonResponse({})
#     response.set_cookie(
#         key='theme',
#         value='dark',
#         max_age=10
#     )
#     return response



def log_out(req):
    try:
        response=JsonResponse({"status":'logged out'})
        response.delete_cookie('username')
        response.delete_cookie('is_logged_in')
        return response
    except:
        return JsonResponse({'status':'logout failed'})
    
