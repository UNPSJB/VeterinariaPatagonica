from django.shortcuts import render_to_response

def verdemo(request):
    template = request.path.split('/')[-1]
    return render_to_response("demos/" + template, request)

def base(request):
    return render_to_response('sitio_base.html',request)
