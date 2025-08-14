import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    smtp_server="smtp.gmail.com"
    port=587
    username="chatterplusapp@gmail.com" 
    password="gqld grzr chce ycnu"
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()  # Seguridad TLS
        server.login(username, password)
        server.send_message(msg)
        print("📨 Email enviado con éxito")