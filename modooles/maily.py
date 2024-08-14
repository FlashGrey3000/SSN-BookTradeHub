import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()
my_mail = os.getenv("MY_MAIL")
my_pass = os.getenc("MY_PASS")

OWNER = my_mail

def send_mailTo(emailID):
    content = EmailMessage()
    content["Subject"]="Sign up at Book Trade Hub Successful!"
    content["From"]=OWNER
    content["To"]=emailID
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(OWNER, my_pass) #Your password
    content.set_content('Thank you for registering with SSN Book Trade Hub!\nStart trading your books with your fellow college peers! Interact with all types of readers. Whether the book be academic or a light-novel we welcome everyone!')
    s.send_message(content)
    s.quit()

def notify_trade(emailID, r_name, o_name, book):
    subject = "New Trade Offer Received on Book Trade Hub!"
    body = f"""
Hello {r_name},

We are excited to inform you that you've received a trade offer on one of your listed books on the Book Trade Hub!

Details of the Trade Offer:
- Offered By: {o_name}
- Book Title: {book}

To view the full details of this trade offer and to respond, please log in to your account on the Book Trade Hub. 

Here's a quick link to your trade offers page: SSN-BTH (This link will not work)

Remember, engaging in trades is a fantastic way to discover new stories while sharing your love for books with others. Please review the offer at your earliest convenience and feel free to reach out to the offerer for any clarifications or negotiations.

If you have any questions or need assistance, our support team is always here to help. Contact us at Discord: XXXXXXX.

Thank you for being a valued member of our book trading community. Happy trading!

Best Regards,
SSN Book Trade Hub
YOUR MAIL

Please note: This is an automated email. Do not reply directly to this message. For support, please use the contact information provided above.
"""
    content = EmailMessage()
    content["Subject"]=subject
    content["From"]=OWNER
    content["To"]=emailID
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(OWNER, my_pass) #Your password
    content.set_content(body)
    s.send_message(content)
    s.quit()
