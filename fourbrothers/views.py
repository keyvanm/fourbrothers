from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from user_manager.forms import ContactUsForm


def index_view(request):
    if request.user.is_authenticated():
        if request.user.profile.type == 'technician':
            return redirect('/dashboard/technician')
        elif request.user.profile.type == 'manager':
            return redirect('/dashboard/manager')
        else:
            return render(request, 'index.html')
    else:
        return render(request, 'index.html')


def terms_view(request):
    return render(request, 'terms.html')


def contact_us(request):
    if request.method == "GET":
        return render(request, 'static-content/contact.html', context={'form': ContactUsForm()})
    if request.method == "POST":
        form = ContactUsForm(request.POST)
        if form.is_valid():
            send_mail(form.cleaned_data['subject'], form.cleaned_data['message'], form.cleaned_data['email'],
                      "adam@fourbrothers.ca", fail_silently=False)
            messages.success(request, "Thank you for contacting us!")
            return redirect('contact')
        return render(request, 'static-content/contact.html', context={'form': form})
