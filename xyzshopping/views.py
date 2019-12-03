from django.shortcuts import render

def HomeView(request):
    return render(request, 'index.html')

def Comming_soon(request):
    return render(request, 'comming_soon.html')

def custom_404(request, exception):
    data = {}
    return render(request, 'tickets/404.html', data)