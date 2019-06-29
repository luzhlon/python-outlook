import email
import imaplib
import smtplib
import datetime
import email.mime.multipart
import config

def decode_header(t):
    value, charset = email.header.decode_header(t)[0]
    if charset:
        value = value.decode(charset)
    return value

def today():
    date = datetime.datetime.now()-datetime.timedelta(1)
    return date.strftime("%d-%b-%Y")

def since_today():
    return '(SINCE "' + today() + '")'

class Message:
    def __init__(self, text):
        assert type(text) is str
        # self.email_message = \ # -> email.EmailMessage
            # email.message_from_string(text, policy = email.policy.default)
        self.message = email.message_from_string(text) # -> email.Message

    # key: Subject, From, To, ...
    def get_header(self, key):
        return decode_header(self.message.get(key))

    def subject(self):
        return self.get_header('Subject')

    def reply_to(self):
        return self.get_header('Reply-To')

    def return_path(self):
        return self.get_header('Return-Path')

    def body(self):
        result = []
        def parse(payload):
            if payload.is_multipart():
                for i in payload.get_payload():
                    parse(i)
            else:
                b = payload.get_payload(decode = True)
                # TODO: Auto detect encoding
                try:
                    result.append(b.decode('utf-8'))
                except UnicodeDecodeError:
                    result.append(b.decode('gbk'))
        parse(self.message)
        return '\n'.join(result)

class Outlook():
    def __init__(self):
        self.imap = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
        # self.smtp = smtplib.SMTP('smtp-mail.outlook.com')
        pass

    def login(self, username, password):
        self.username = username
        self.password = password
        while True:
            try:
                r, d = self.imap.login(username, password)
                assert r == 'OK', 'login failed'
                print(" > Sign as ", d[0].decode())
            except Exception as e:
                print(" > Sign In ...", e)
                continue
            break

    def logout(self):
        return self.imap.logout()

    def list(self):
        # self.login()
        return self.imap.list()

    def select(self, str):
        return self.imap.select(str)

    def select_inbox(self):
        return self.imap.select("Inbox")

    def select_junk(self):
        return self.imap.select("Junk")

    def get_ids(self, *args):
        r, d = self.imap.search(None, *args)
        result = d[0].split(b' ')
        # print('get_ids', result)
        return result

    def has_unread(self):
        result = self.get_ids('UNSEEN')
        return len(result)

    def message_generator(self, *args):
        for id in self.get_ids(*args):
            yield self.get_email(id)

    def all_email(self):
        return self.message_generator('ALL')

    def unread(self):
        return self.message_generator('UNSEEN')

    def today(self):
        return self.message_generator(since_today())

    def today_unread(self):
        return self.message_generator(since_today(), 'UNSEEN')

    def today_readed(self):
        return self.message_generator(since_today(), 'SEEN')

    def get_email(self, id):
        r, d = self.imap.fetch(id, "(RFC822)")
        text = d[0][1].decode('utf-8')
        return Message(text)

    # def raw_read(self):
    #     list = self.readed_ids()
    #     latest_id = list[-1]
    #     r, d = self.imap.fetch(latest_id, "(RFC822)")
    #     self.raw_email = d[0][1]
    #     return self.raw_email

    # def readOnly(self, folder):
    #     return self.imap.select(folder, readonly=True)

    # def writeEnable(self, folder):
    #     return self.imap.select(folder, readonly=False)

    # def sendEmailMIME(self, recipient, subject, message):
    #     msg = email.mime.multipart.MIMEMultipart()
    #     msg['to'] = recipient
    #     msg['from'] = self.username
    #     msg['subject'] = subject
    #     msg.add_header('reply-to', self.username)
    #     # headers = "\r\n".join(["from: " + "sms@kitaklik.com","subject: " + subject,"to: " + recipient,"mime-version: 1.0","content-type: text/html"])
    #     # content = headers + "\r\n\r\n" + message
    #     try:
    #         self.smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
    #         self.smtp.ehlo()
    #         self.smtp.starttls()
    #         self.smtp.login(self.username, self.password)
    #         self.smtp.sendmail(msg['from'], [msg['to']], msg.as_string())
    #         print("   email replied")
    #     except smtplib.SMTPException:
    #         print("Error: unable to send email")

    # def sendEmail(self, recipient, subject, message):
    #     headers = "\r\n".join([
    #         "from: " + self.username,
    #         "subject: " + subject,
    #         "to: " + recipient,
    #         "mime-version: 1.0",
    #         "content-type: text/html"
    #     ])
    #     content = headers + "\r\n\r\n" + message
    #     while True:
    #         try:
    #             self.smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
    #             self.smtp.ehlo()
    #             self.smtp.starttls()
    #             self.smtp.login(self.username, self.password)
    #             self.smtp.sendmail(self.username, recipient, content)
    #             print("   email replied")
    #         except:
    #             print("   Sending email...")
    #             continue
    #         break
