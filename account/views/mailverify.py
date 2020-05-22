
current_site = get_current_site(request)
email_subject = 'Activate Your Acc'
message = render_to_string('activate_account.html', {
    'user': user,
    'domain': current_site.domain,
    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    'token': account_activation_token.make_token(user),
})
to_email = form.cleaned_data.get('email')
email = EmailMessage(email_subject, message, to=[to_email],from_email=['hello@google.in'])
email.send()

def send_verification_mail()
