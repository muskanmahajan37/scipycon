from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from project.scipycon.base.models import Event
from project.scipycon.registration.forms import RegistrationEditForm
from project.scipycon.registration.forms import RegistrationSubmitForm
from project.scipycon.registration.forms import WifiForm
from project.scipycon.registration.models import Registration
from project.scipycon.registration.models import Wifi
from project.scipycon.registration.utils import send_confirmation
from project.scipycon.user.forms import RegistrantForm
from project.scipycon.user.models import UserProfile
from project.scipycon.user.utils import scipycon_createregistrant
from project.scipycon.utils import set_message_cookie


REG_TOTAL = 1000


@login_required
def registrations(request, scope, 
                  template_name='registration/registrations.html'):
    """Simple page to count registrations"""

    registrations = Registration.objects.all().count()

    user = request.user
    if user.is_authenticated():
        registration = Registration.objects.get(registrant=user)
    else:
        registration = None

    event = Event.objects.get(scope=scope)

    return render_to_response(template_name, RequestContext(request, {
        'params': {'scope': scope},
        'over_reg' : registrations >= REG_TOTAL and True or False,
        'registrations' : registrations,
        'registration': registration,
        'event': event}))

@login_required
def edit_registration(request, scope, id,
                      template_name='registration/edit-registration.html'):
    """Allows users that submitted a registration to edit it.
    """

    reg = Registration.objects.get(pk=id)
    wifi = Wifi.objects.get(user=reg.registrant)

    if reg.registrant != request.user:
        redirect_to = reverse('scipycon_account', kwargs={'scope': scope})

        return set_message_cookie(
            redirect_to,
            msg = u'Redirected because the registration you selected' \
                      + ' is not your own.')

    if request.method == 'POST':
        registration_form = RegistrationEditForm(data=request.POST)
        wifi_form = WifiForm(data=request.POST)

        if registration_form.is_valid() and wifi_form.is_valid():
            reg.organisation = registration_form.data.get('organisation')
            reg.occupation = registration_form.data.get('occupation')
            reg.city = registration_form.data.get('city')
            reg.phone_num = registration_form.data.get('phone_num')
            reg.postcode = registration_form.data.get('postcode')
            #reg.tshirt = registration_form.data.get('tshirt')
            reg.allow_contact = registration_form.data.get(
                'allow_contact') and True or False
            reg.conference = registration_form.data.get(
                'conference') and True or False
            reg.tutorial = registration_form.data.get(
                'tutorial') and True or False
            reg.sprint = registration_form.data.get(
                'sprint') and True or False
            reg.save()

            wifi = wifi_form.save(reg.registrant, reg.scope)

            # Saved.. redirect
            redirect_to = reverse('scipycon_account', kwargs={'scope': scope})

            return set_message_cookie(redirect_to,
                msg = u'Your changes have been saved.')
        else:
            import logging
            logging.error(registration_form.data)
            raise "Bow Bow"
    else:
        registration_form = RegistrationEditForm(initial={
            'id' : id,
            'organisation' : reg.organisation,
            'occupation' : reg.occupation,
            'city' : reg.city,
            'phone_num': reg.phone_num,
            #'tshirt' : reg.tshirt,
            'conference': reg.conference,
            'tutorial': reg.tutorial,
            'postcode' : reg.postcode,
            'sprint' : reg.sprint,
            'allow_contact' : reg.allow_contact,
            })
        wifi_form = WifiForm(initial={
            'user': wifi.user,
            'scope': wifi.scope,
            'wifi': wifi.wifi
            })

    return render_to_response(
        template_name, RequestContext(request, {
        'params': {'scope': scope},
        'registration': {'id': id},
        'registration_form': registration_form,
        'wifi_form': wifi_form}))

def submit_registration(request, scope,
        template_name='registration/submit-registration.html'):
    """Allows user to edit registration
    """

    user = request.user
    reg_count = Registration.objects.all().count()

    scope_entity = Event.objects.get(scope=scope)

    if user.is_authenticated():
        try:
            profile = user.get_profile()
        except:
            profile, new = UserProfile.objects.get_or_create(
                user=user, scope=scope_entity)
            if new:
                profile.save()
        try:
            registration = Registration.objects.get(registrant=user)
            if registration:
                redirect_to = reverse('scipycon_account',
                                      kwargs={'scope': scope})
                return set_message_cookie(
                    redirect_to, msg = u'You have already been registered.')

        except ObjectDoesNotExist:
            pass

    message = None

    if request.method == 'POST':
        registration_form = RegistrationSubmitForm(data=request.POST)
        registrant_form = RegistrantForm(data=request.POST)
        wifi_form = WifiForm(data=request.POST)

        if request.POST.get('action', None) == 'login':
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():

                login(request, login_form.get_user())

                redirect_to = reverse('scipycon_submit_registration',
                                      kwargs={'scope': scope})
                return set_message_cookie(redirect_to,
                        msg = u'You have been logged in please continue' + \
                               'with registration.')

        newuser = None
        passwd = None
        if not user.is_authenticated():
            if registrant_form.is_valid():
                newuser = scipycon_createregistrant(
                    request, registrant_form.data, scope)

                # Log in user
                passwd = User.objects.make_random_password()
                newuser.set_password(passwd)
                newuser.save()

                user = authenticate(username=newuser.username, password=passwd)

                login(request, user)

                newuser = user

        else:
            newuser = user

        if registration_form.is_valid() and newuser and wifi_form.is_valid():
            allow_contact = registration_form.cleaned_data.get(
                'allow_contact') and True or False
            conference = registration_form.cleaned_data.get(
                'conference') and True or False
            tutorial = registration_form.cleaned_data.get('tutorial') and \
                True or False
            sprint = registration_form.cleaned_data.get('sprint') and \
                True or False

            registrant = User.objects.get(pk=newuser.id)

            reg = Registration(
                scope=scope_entity,
                registrant = registrant,
                organisation = registration_form.cleaned_data.get(
                    'organisation'),
                occupation = registration_form.cleaned_data.get('occupation'),
                city = registration_form.cleaned_data.get('city'),
                #tshirt = registration_form.data.get('tshirt'),
                postcode = registration_form.cleaned_data.get('postcode'),
                phone_num = registration_form.cleaned_data.get('phone_num'),
                allow_contact = allow_contact,
                conference = conference,
                tutorial = tutorial,
                sprint = sprint)
            reg.save() 

            # get id and use as slug and invoice number
            id = reg.id
            slug = 'SCIPYIN2010%04d' % id
            reg.slug = slug
            reg.save()

            wifi = wifi_form.save(registrant, scope_entity)

            send_confirmation(registrant, scope_entity,password=passwd)

            redirect_to = reverse('scipycon_registrations',
                                  kwargs={'scope': scope})
            return set_message_cookie(redirect_to,
                    msg = u'Thank you, your registration has been submitted '\
                           'and an email has been sent with payment details.')

    else:
        registration_form = RegistrationSubmitForm()
        registrant_form = RegistrantForm()
        wifi_form = WifiForm()

    login_form = AuthenticationForm()


    return render_to_response(template_name, RequestContext(request, {
        'params': {'scope': scope},
        'registration_form': registration_form,
        'registrant_form' : registrant_form,
        'over_reg' : reg_count >= REG_TOTAL and True or False,
        'wifi_form' : wifi_form,
        'message' : message,
        'login_form' : login_form
    }))


@login_required
def regstats(request, scope,
                 template_name='registration/regstats.html'):
    """View that gives the statistics of registrants.
    """
    from project.scipycon.registration.forms import RegistrationAdminSelectForm
    if not request.user.is_staff:
        redirect_to = reverse('scipycon_login', kwargs={'scope': scope})

    if request.method == "POST":
        form = RegistrationAdminSelectForm(request.POST)
        if form.is_valid():
            conference = form.cleaned_data['by_conference']
            tutorial = form.cleaned_data['by_tutorial']
            sprint = form.cleaned_data['by_sprint']
            include = form.cleaned_data['include']

            q = Registration.objects.all()
            q = q.filter(conference=conference)
            q = q.filter(tutorial=tutorial)
            q = q.filter(sprint=sprint)

            q = q.order_by('registrant__email')

            query = q.query
            results = list(q)

            if include == []:
                # default to include all fields
                include = [i[0] for i in IC]
            if results:
                response = HttpResponse(mimetype='text/csv')
                response['Content-Disposition'] = 'attachment; filename=registrations.csv'
                output = csv.writer(response)
                output.writerow([h for h in include])
                for row in results:
                    conference = row.conference == True and 'yes' or 'no'
                    tutorial = row.tutorial == True and 'yes' or 'no'
                    sprint = row.sprint == True and 'yes' or 'no'
                    wrow = []
                    if 'Name' in include:
                        wrow.append(
                            row.registrant.get_full_name().encode('utf-8'))
                    if 'Email' in include:
                        wrow.append(row.registrant.email.encode('utf-8'))
                    if 'Organisation' in include:
                        wrow.append(row.organisation.encode('utf-8'))
                    if 'Conference' in include:
                        wrow.append(conference)
                    if 'Tutorial' in include:
                        wrow.append(tutorial)
                    if 'Sprint' in include:
                        wrow.append(sprint)
                    output.writerow(wrow)
                return response
            else:
                no_results = u'No results found for the query'

    else:
        form = RegistrationAdminSelectForm()
    return render_to_response(template_name, RequestContext(request,
        locals()))
