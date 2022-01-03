import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template
EMAIL_ADDRESS = 'noReplyProxi@gmail.com'
EMAIL_PASSWORD = 'proxiNoReply'
PROXI_DOMAIN = 'localhost:4200'

#REGISTRATION EMAIL
with open('C:/Users/nicol/OneDrive/Documents/Coding/Other/Proxi Website/backend/flask_proxi/mail_sys/templates/register/register_verification.txt', 'r') as file:
    reg_ver_txt_file = file.read().replace('\n', '')
with open('C:/Users/nicol/OneDrive/Documents/Coding/Other/Proxi Website/backend/flask_proxi/mail_sys/templates/register/register_verification_html.txt', 'r') as file:
    reg_ver_html_file = file.read().replace('\n', '')

#NEW CHAT INVITE EMAIL

def sendSMTP_mail(sender, password, receiver, message, email_use):
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender, password)
        server.sendmail(
            sender, receiver, message.as_string()
        )
    print("Send email to: {} {}".format(receiver, email_use))

def send_confirmation_of_email(reciever, password, sender_email, proxi_domain_base, code):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verification Code"
    message["From"] = sender_email
    message["To"] = reciever

    proxiHelpLink = proxi_domain_base + '/help'
    proxiCodeLink = proxi_domain_base + '/api/verify?email={}&code={}&origin={}'.format(reciever, code, "email")

    text_rendered = reg_ver_txt_file.format(proxiCodeLink, code, proxiHelpLink)
    html_rendered = reg_ver_html_file.format(proxiCodeLink, code, proxiHelpLink)

    part1 = MIMEText(text_rendered, "plain")
    part2 = MIMEText(html_rendered, "html")

    message.attach(part1)
    message.attach(part2)

    sendSMTP_mail(sender_email, password, reciever, message, 'VERIFICATION EMAIL. CODE => {}'.format(code))
