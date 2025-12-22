from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def chatbot_page(request):
    return render(request, "api/chat.html")
