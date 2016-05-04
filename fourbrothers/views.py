from django.contrib import messages
from django.core.mail.message import EmailMultiAlternatives
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
            email_body = "{0} {1} ({2}) \n {3}".format(form.cleaned_data['first_name'],
                                                       form.cleaned_data['last_name'],
                                                       form.cleaned_data['email'],
                                                       form.cleaned_data['message'])
            html_email_body = "<p>{0} {1} ({2})</p><p>{3}<p>".format(form.cleaned_data['first_name'],
                                                                     form.cleaned_data['last_name'],
                                                                     form.cleaned_data['email'],
                                                                     form.cleaned_data['message'])
            email = EmailMultiAlternatives(form.cleaned_data['subject'],
                                           email_body,
                                           form.cleaned_data['email'],
                                           ("adam@fourbrothers.ca",),
                                           reply_to=(form.cleaned_data['email'],))
            email.attach_alternative(html_email_body, "text/html")
            email.send()
            messages.success(request, "Thank you for contacting us! We will try to respond as soon as possible.")
            return redirect('contact')
        return render(request, 'static-content/contact.html', context={'form': form})
