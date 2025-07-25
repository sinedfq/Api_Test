from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ref.models import User
import time

def phone_auth(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if phone and phone.startswith('+') and phone[1:].isdigit():
            request.session['auth_phone'] = phone
            return redirect('code_auth')
        else:
            messages.error(request, 'Неверный формат номера телефона')
    return render(request, 'ref/phone_auth.html')

def code_auth(request):
    phone = request.session.get('auth_phone')
    if not phone:
        return redirect('phone_auth')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        if code and len(code) == 4 and code.isdigit():
            time.sleep(1)  # Имитация задержки
            
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={'username': phone}
            )
            
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Неверный код подтверждения')
    
    return render(request, 'ref/code_auth.html', {'phone': phone})

@login_required
def profile(request):
    referred_users = User.objects.filter(
        activated_invite_code=request.user.invite_code
    ).values_list('phone', flat=True)
    
    return render(request, 'ref/profile.html', {
        'user': request.user,
        'referred_users': referred_users
    })

@login_required
def activate_invite(request):
    if request.user.activated_invite_code:
        messages.warning(request, 'Вы уже активировали инвайт-код')
        return redirect('profile')
    
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        
        try:
            referrer = User.objects.get(invite_code=invite_code)
            if referrer == request.user:
                messages.error(request, 'Нельзя активировать свой собственный инвайт-код')
            else:
                request.user.activated_invite_code = invite_code
                request.user.save()
                messages.success(request, 'Инвайт-код успешно активирован')
                return redirect('profile')
        except User.DoesNotExist:
            messages.error(request, 'Инвайт-код не найден')
    
    return render(request, 'ref/activate_invite.html')