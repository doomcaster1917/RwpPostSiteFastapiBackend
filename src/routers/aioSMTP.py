#!/usr/bin/env python3
from email.mime.text import MIMEText
import aiosmtplib
from src.config import SMTP_USER, SMTP_PASSWORD

MAIL_PARAMS = {'TLS': True, 'host': 'smtp.yandex.ru',
               'password': SMTP_PASSWORD,
               'user': SMTP_USER, 'port': 587}
async def send_mail_async(sender, to, subject, secure_code, **params):
    mail_params = params.get("mail_params", MAIL_PARAMS)
    msg = MIMEText(str(secure_code))
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(to)

    host = mail_params.get('host')
    isSSL = mail_params.get('SSL', False)
    STARTTLS = mail_params.get('STARTTLS', True)
    port = mail_params.get('port')
    smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=isSSL, start_tls=STARTTLS)
    await smtp.connect()
    if 'user' in mail_params:
        await smtp.login(mail_params['user'], mail_params['password'])
    await smtp.send_message(msg, recipients=to)
    await smtp.quit()
    return True

