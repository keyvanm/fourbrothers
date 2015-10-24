from itertools import izip_longest
from django.contrib.auth.decorators import login_required
from django.http.response import Http404


class ManagerPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.type != 'manager':
            raise Http404
        else:
            return super(ManagerPermissionMixin, self).dispatch(request)


class ManagerTechnicianPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.type == 'technician' or request.user.profile.type == 'manager':
            return super(ManagerTechnicianPermissionMixin, self).dispatch(request)
        else:
            raise Http404



class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)