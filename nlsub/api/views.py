from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseBadRequest
from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, parser_classes, authentication_classes
from rest_framework.exceptions import ParseError, APIException
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from api.email import send_subscription_email, validate_confirm, send_email
from api.models import List, Subscriber


def validateEmail( email ):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

@api_view(['POST'])
@parser_classes((JSONParser,))
@authentication_classes((),)
def subscribe(request, list_id):
    try:
        list_model = List.objects.get(pk=int(list_id))
    except List.DoesNotExist:
        raise ParseError("The list you subscribe to does not exist")
    #try:
    if validateEmail(request.data['email']):
        try:
            send_subscription_email(request.data['email'], list_model)
            return Response({"result":"ok"})
        except APIException:
            return Response({"result":"ok", "detail": "Already subcribed"})
    #except KeyError:
    # TODO: Nicer error page
    #   pass
    raise ParseError("Email in an invalid format")

@api_view(['POST','GET'])
def confirm_subscribe(request):
    try:
        signature =  request.GET['signature']
    except MultiValueDictKeyError:
        raise ParseError("GET parameter signature is missing")
    signed = validate_confirm("subscribe", signature)
    email = signed[0]
    elist = List.objects.get(pk=int(signed[1]))
    context = {"title": "Successfully subscribed",
               "email": signed[0],
               "list": elist,
               "url": request.get_full_path()}
    if request.method == 'GET':
        return TemplateResponse(request, 'ask.html', context)
    try:
        sub = Subscriber(email=email, list=elist)
        sub.save()
    except IntegrityError:
        context["title"] = "Already subscribed"
        return TemplateResponse(request, "err_alr_sub.html", context)
    return TemplateResponse(request, "subscribed.html", context)

@api_view(['POST','GET'])
def confirm_unsubscribe(request):
    signed = []
    try:
        signed = validate_confirm("unsubscribe", request.GET['signature'])
    except MultiValueDictKeyError:
        raise ParseError("Signature is missing.")
    email = signed[0]
    list = List.objects.get(pk=signed[1])
    context = {"title": "Successfully unsubscribed",
               "email": signed[0],
               "list": list,
               "url": request.get_full_path()}
    if request.method == 'GET':
        return TemplateResponse(request, 'ask.html', context)
    try:
        sub = Subscriber.objects.get(email=email, list=list)
        sub.delete()
    except Subscriber.DoesNotExist:
        context["title"] = "Already unsubscribed"
        return TemplateResponse(request, "err_alr_unsub.html", context)
    return TemplateResponse(request, "unsubscribed.html", context)

@api_view(['POST'])
@parser_classes((JSONParser,))
@authentication_classes((TokenAuthentication,),)
@login_required
def send(request):
    '''
    html, list, subject
    :param request:
    :return:
    '''
    if not request.user:
        return
    try:
        html = str(request.data['html'])
        list_id = int(request.data['list'])
        subject = str(request.data['subject'])
        elist = List.objects.get(pk=list_id)
    except:
        #TODO All error handling
        raise
    for subscriber in Subscriber.objects.filter(list_id=list_id):
        send_email(subscriber, elist, html, subject)
    return Response({"response": "ok"})
