'''
from django.shortcuts import render_to_response

from django.template import loader
from django.http import HttpResponse

    def verdemo(request):
        context = {}
        template = request.path.split('/')[-1]
        #printf(template)
        tmp = loader.get_template('demos/'+template)
        #return render_to_response("demos/" + template, request)
        return HttpResponse(tmp.render(context, request))

def base(request):
    return render_to_response('sitio_base.html',request)
    '''
from django.shortcuts import render_to_response

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse


def verdemo(request):
    template = request.path.split('/')[-1]
    return render_to_response("demos/" + template, request)

def base(request):
    #[BUG]no funciona con render_to_response.
    #return render_to_response("sitio_base.html",request)
    context = {}#Defino un contexto.
    template = loader.get_template('sitio_base.html')#Cargo el template del sitio base.
    return HttpResponse(template.render(context,request))#Devuelvo la url con el template armado.
