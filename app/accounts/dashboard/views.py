import random
import string
import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from .forms import UserInfoForm, SettingsForm
from accounts.models import User


@login_required(login_url='login')
def favorites_view(request):
    if request.headers.get('Hx-Request') == 'true':
        return render(request, 'accounts/dashboard/favorites.html')
    return render(request, 'base/base_dashboard.html', {
        'tab': 'favorites'
    })


@login_required(login_url='login')
def user_info_view(request):
    user = request.user

    if request.method == 'GET':
        if not request.GET.get('pending'):
            for key in ('new_email', 'email_code', 'email_code_ts'):
                request.session.pop(key, None)

    ts = request.session.get('email_code_ts')
    if ts and (datetime.datetime.now().timestamp() - ts > settings.SIGNUP_CODE_EXPIRATION_SECONDS):
        for key in ('new_email', 'email_code', 'email_code_ts'):
            request.session.pop(key, None)
        messages.warning(request, "Срок действия кода подтверждения email истек. Попробуйте ещё раз")

    if request.method == 'POST':
        form = UserInfoForm(request.POST, user=user, session=request.session)

        new_email = request.POST.get('email')
        old_email = user.email

        if new_email and new_email != old_email and not request.session.get('new_email'):
            if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
                if request.headers.get('Hx-Request') == 'true':
                    return render(request, 'accounts/dashboard/user_info.html', {'form': form})
                else:
                    messages.error(request, "Этот email уже используется. Пожалуйста введите другой")
                    return redirect('dashboard:user_info')

            code = ''.join(random.choices(string.digits, k=6))
            request.session['new_email'] = new_email
            request.session['email_code'] = code
            request.session['email_code_ts'] = datetime.datetime.now().timestamp()

            subject = f"Код подтверждения для смены email на {settings.SITE_NAME}"
            text_body = render_to_string('email/dashboard/change_email_code.txt', {
                'username': user.username,
                'code': code,
            })

            html_body = render_to_string('email/dashboard/change_email_code.html', {
                'username': user.username,
                'code': code,
            })

            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [new_email]

            msg = EmailMultiAlternatives(subject, text_body, from_email, to_email)
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)

            messages.info(request, "На указанный email отправлен код подтверждения. "
                                   "Введите его, чтобы подтвердить смену адреса. Не покидайте эту страницу.")

            target = reverse('dashboard:user_info') + '?pending=1'
            if request.headers.get('Hx-Request') == 'true':
                resp = HttpResponse(status=204)
                resp.headers['HX-Redirect'] = target
                return resp
            else:
                return redirect(target)

        if form.is_valid():
            form.save()
            messages.success(request, "Данные успешно обновлены")
            if form.cleaned_data.get('new_password1'):
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)

            if request.headers.get('Hx-Request') == 'true':
                resp = HttpResponse(status=204)
                resp.headers['HX-Redirect'] = reverse('dashboard:user_info')
                return resp
            else:
                return redirect('dashboard:user_info')

        else:
            if request.headers.get('Hx-Request') == 'true':
                return render(request, 'accounts/dashboard/user_info.html', {'form': form})
            return redirect('dashboard:user_info')

    # GET
    form = UserInfoForm(user=user, session=request.session)
    if request.headers.get('Hx-Request') == 'true':
        return render(request, 'accounts/dashboard/user_info.html', {'form': form})
    return render(request, 'base/base_dashboard.html', {
        'tab': 'user_info',
        'form': form
    })


@login_required(login_url='login')
def settings_view(request):
    user = request.user

    if request.method == 'POST':
        form = SettingsForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Настройки сохранены")
            if request.headers.get('Hx-Request') == 'true':
                resp = HttpResponse(status=204)
                resp.headers['HX-Redirect'] = reverse('dashboard:settings')
                return resp
            return redirect('dashboard:settings')
        else:
            if request.headers.get('Hx-Request') == 'true':
                return render(request, 'accounts/dashboard/settings.html', {'form': form})
            return redirect('dashboard:settings')

    # GET
    form = SettingsForm(user=user)
    if request.headers.get('Hx-Request') == 'true':
        return render(request, 'accounts/dashboard/settings.html', {'form': form})
    return render(request, 'base/base_dashboard.html', {
        'tab': 'settings',
        'form': form
    })
