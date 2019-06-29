
import outlook
import os

password = os.environ.get('OUTLOOK_PASSWORD')
password = password if password else input('Password(OUTLOOK_PASSWORD): ')

mail = outlook.Outlook()
mail.login('luzhlon@outlook.com', password)

mail.select_inbox()
for m in mail.today():
    print('From:', m.get_header('From'))
    print('To:', m.get_header('To'))
    print('Subject:', m.subject())
    print('')
    print(m.body())

    print('')
    print('------------------------------------------------------------')
    print('')
