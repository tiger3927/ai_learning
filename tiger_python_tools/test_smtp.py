import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
from email.header import Header
from email import encoders
import os,time,re
import mimetypes

def SendMail(sender = '914843402@qq.com',
             receiver = '914843402@qq.com',
             subject = '',
             textcontent=None,
             htmlcontent=None,
             attachfilenamelist=[],
             smtpserver = 'smtp.qq.com',
             username = '914843402',
             password = 'izlvckkmrugjbcag'):

    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    if (textcontent!=None):
        part1 = MIMEText(textcontent, 'plain')
        msgRoot.attach(part1)
    if (htmlcontent != None):
        part2 = MIMEText(htmlcontent, 'html')
        msgRoot.attach(part2)
    '''
    img1 = MIMEImage(open(pic_path, 'rb').read(), _subtype='octet-stream')
    img1.add_header('Content-ID', 'image1')
    msgRoot.attach(img1)
    '''
    for f in attachfilenamelist:
        ctype, encoding = mimetypes.guess_type(f)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype,subtype=ctype.split('/')
        filepath, filename = os.path.split(f)
        with open(f, 'rb') as fp:
            mb = MIMEBase(maintype,subtype)
            mb.set_payload(fp.read())
            mb.add_header('Content-Disposition', 'attachment', filename=filename)  # 修改邮件头
            encode_base64(mb)
            msgRoot.attach(mb)

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msgRoot.as_string())
    smtp.quit()

if __name__=="__main__":
    directory="C:\\Users\\tiger\\Desktop"
    filenames=[]
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        filenames.append(path)

    sendmail(subject="start mail",textcontent="content",attachfilenamelist=filenames)




