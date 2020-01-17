import smtplib
import uuid
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template, url_for
from itsdangerous import URLSafeTimedSerializer

TEST_MESSAGES = []


class EmailService:

    def __init__(self, app):
        self.app = app
        self.api_url = app.config['API_URL']
        self.site_url = app.config['SITE_URL']
        self.admin_email = app.config['ADMIN_EMAIL']
        self.principal_investigator_email = app.config['PRINCIPAL_INVESTIGATOR_EMAIL']

    def tracking_code(self):
        return str(uuid.uuid4())[:16]

    def email_server(self):
        server = smtplib.SMTP(host=self.app.config['MAIL_SERVER'],
                              port=self.app.config['MAIL_PORT'],
                              timeout=self.app.config['MAIL_TIMEOUT'])
        server.ehlo()
        if self.app.config['MAIL_USE_TLS']:
            server.starttls()
        if self.app.config['MAIL_USERNAME']:
            server.login(self.app.config['MAIL_USERNAME'],
                         self.app.config['MAIL_PASSWORD'])
        return server

    def send_email(self, subject, recipients, text_body, html_body, sender=None, ical=None):
        msgRoot = MIMEMultipart('related')
        msgRoot.set_charset('utf8')

        if (sender == None):
            sender = self.app.config['MAIL_DEFAULT_SENDER']

        msgRoot['Subject'] = Header(subject.encode('utf-8'), 'utf-8').encode()
        msgRoot['From'] = sender
        msgRoot['To'] = ', '.join(recipients)
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        part1 = MIMEText(text_body, 'plain', _charset='UTF-8')
        part2 = MIMEText(html_body, 'html', _charset='UTF-8')

        msgAlternative.attach(part1)
        msgAlternative.attach(part2)

        if ical:
            ical_atch = MIMEText(ical.decode("utf-8"),'calendar')
            ical_atch.add_header('Filename','event.ics')
            ical_atch.add_header('Content-Disposition','attachment; filename=event.ics')
            msgRoot.attach(ical_atch)

        if 'TESTING' in self.app.config and self.app.config['TESTING']:
            print("TEST:  Recording Emails, not sending - %s - to:%s" % (subject, recipients))
            TEST_MESSAGES.append(msgRoot)
            return

        server = self.email_server()
        server.sendmail(sender, recipients, msgRoot.as_bytes())
        server.quit()

    def confirm_email(self, user):
        user.token_url = ''
        ts = URLSafeTimedSerializer(self.app.config["SECRET_KEY"])
        token = ts.dumps(user.email, salt='email-reset-key')
        role = '' + user.role.name + '/'
        tracking_code = self.tracking_code()

        subject = "Autism DRIVE: Confirm Email"
        confirm_url = self.app.config['FRONTEND_EMAIL_RESET'] + role + token
        logo_url = url_for('track.logo', user_id=user.id, code=tracking_code, _external=True)
        text_body = render_template("confirm_email.txt",
                                    user=user, confirm_url=confirm_url,
                                    forgot_pass_url=self.app.config['FRONTEND_FORGOT_PASSWORD'],
                                    tracking_code=tracking_code)

        html_body = render_template("confirm_email.html",
                                    user=user, confirm_url=confirm_url,
                                    forgot_pass_url=self.app.config['FRONTEND_FORGOT_PASSWORD'],
                                    logo_url=logo_url,
                                    tracking_code=tracking_code)

        self.send_email(subject,
                        recipients=[user.email], text_body=text_body, html_body=html_body)

        if self.app.config.get('TESTING') or self.app.config.get('DEVELOPMENT'):
            user.token_url = confirm_url

        return tracking_code

    def reset_email(self, user):
        user.token_url = ''
        ts = URLSafeTimedSerializer(self.app.config["SECRET_KEY"])
        token = ts.dumps(user.email, salt='email-reset-key')
        role = '' + user.role.name + '/'
        tracking_code = self.tracking_code()

        subject = "Autism DRIVE: Password Reset Email"
        reset_url = self.app.config['FRONTEND_EMAIL_RESET'] + role + token
        logo_url = url_for('track.logo', user_id=user.id, code=tracking_code, _external=True)
        text_body = render_template("reset_email.txt",
                                    user=user, reset_url=reset_url,
                                    forgot_pass_url=self.app.config['FRONTEND_FORGOT_PASSWORD'],
                                    tracking_code=tracking_code)

        html_body = render_template("reset_email.html",
                                    user=user, reset_url=reset_url,
                                    forgot_pass_url=self.app.config['FRONTEND_FORGOT_PASSWORD'],
                                    logo_url=logo_url,
                                    tracking_code=tracking_code)

        self.send_email(subject,
                        recipients=[user.email], text_body=text_body, html_body=html_body)

        if self.app.config.get('TESTING') or self.app.config.get('DEVELOPMENT'):
            user.token_url = reset_url

        return tracking_code

    def study_inquiry_email(self, study, user):
        tracking_code = self.tracking_code()

        subject = "Autism DRIVE: Study Inquiry Email"
        logo_url = url_for('track.logo', user_id=user.id, code=tracking_code, _external=True)
        text_body = render_template("study_inquiry_email.txt",
                                    user=user, study=study,
                                    user_detail_url=self.site_url + '/#/admin/user/' + str(user.id),
                                    tracking_code=tracking_code)

        html_body = render_template("study_inquiry_email.html",
                                    user=user, study=study,
                                    user_detail_url=self.site_url + '/#/admin/user/' + str(user.id),
                                    logo_url=logo_url,
                                    tracking_code=tracking_code)

        self.send_email(subject,
                        recipients=[study.coordinator_email, 'autismdrive@virginia.edu'], text_body=text_body, html_body=html_body)

        return tracking_code

    def admin_alert_email(self, subject, message, alert_principal_investigator=False):
        with self.app.app_context():
            context = {}
            text_body = render_template("admin_email.txt", msg=message, site_url=self.site_url, **context)
            html_body = render_template("admin_email.html", msg=message, site_url=self.site_url, **context)
            recipients = [self.admin_email]
            if alert_principal_investigator:
                recipients.append(self.principal_investigator_email)

            self.send_email(subject,
                            recipients=recipients, text_body=text_body, html_body=html_body)
