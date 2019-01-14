import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_reset_link(receiver_email, link):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "JJVideo2019@gmail.com"  # Enter your address  # Enter receiver address
    password = "JJRulez2019!"
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset password"
    message["From"] = sender_email
    message["To"] = receiver_email
    # Create the plain-text and HTML version of your message
    text = "Hello, follow this link to reset your password " + link
    html = """\
    <html>
      <body>
        <p>Hello,<br>
           follow this link to reset your password:<br>
           <a href="{0}">reset password</a>

        </p>
      </body>
    </html>
    """.format(link)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
