from django.shortcuts import render, redirect


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
