import base64
import functions_framework
import urllib.request
import json
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.text import MIMEText
import smtplib

def getemailmessage (KEY,link,strategy):
    url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={link}&strategy={strategy}&locale=en&key={KEY}"
#Note that you can insert your URL with the parameter URL and you can also modify the device parameter if you would like to get the data for desktop.
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())  
    # fcp = data["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["percentile"]/1000
    # fid = data["loadingExperience"]["metrics"]["FIRST_INPUT_DELAY_MS"]["percentile"]/1000
    # lcp = data["loadingExperience"]["metrics"]["LARGEST_CONTENTFUL_PAINT_MS"]["percentile"]
    # cls = data["loadingExperience"]["metrics"]["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["percentile"]/100
    # inp = data["loadingExperience"]["metrics"]["INTERACTION_TO_NEXT_PAINT"]["percentile"]
    # ttfb = data["loadingExperience"]["metrics"]["EXPERIMENTAL_TIME_TO_FIRST_BYTE"]["percentile"]/1000
    try:
        fcp_score = data["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["category"]
    except KeyError:
        fcp_score = "NA"
    try:
        fid_score = data["loadingExperience"]["metrics"]["FIRST_INPUT_DELAY_MS"]["category"]
    except KeyError:
            fid_score = "NA"
    try:
        lcp_score = data["loadingExperience"]["metrics"]["LARGEST_CONTENTFUL_PAINT_MS"]["category"]
    except KeyError:
        lcp_score = "NA"
    try:
        cls_score = data["loadingExperience"]["metrics"]["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["category"]
    except KeyError:
        cls_score = "NA"
    try:
        inp_score = data["loadingExperience"]["metrics"]["INTERACTION_TO_NEXT_PAINT"]["category"]
    except KeyError:
        inp_score = "NA"
    try:
        ttfb_score = data["loadingExperience"]["metrics"]["EXPERIMENTAL_TIME_TO_FIRST_BYTE"]["category"]
    except KeyError:
        ttfb_score = "NA"
    try:
        overall_score = data["lighthouseResult"]["categories"]["performance"]["score"] * 100
    except KeyError:
        overall_score = "NA"

    if overall_score < 60 :
        performance_review = 'failed'
    else: performance_review = 'passed'

    message = "<p>The URL: " + link + " FCP performance is " + fcp_score + ", FID performance is " + fid_score + ", LCP performance is " + lcp_score + ", CLS performance is " + cls_score + ", INP performance is " + inp_score + ", TTFB performance is " + ttfb_score + ', overall performance score is ' + str(overall_score) + ', web performance ' + performance_review

    return message,performance_review
# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    today = date.today()
    today = today.strftime("%d/%m/%Y")
    API_KEY = "AIzaSyArwZK1fEEiUbe9gUILbC0XKZ3yspv0QG8"
    links = ["https://www.printerpix.co.uk/cpg/custom-blanket-mink-touch/","https://www.printerpix.co.uk/personalised-gifts-for-boyfriend-photo-blanket/","https://www.printerpix.co.uk/captioned-photo-book/",
        "https://www.printerpix.co.uk/cpg/custom-photo-book-hardcover/","https://www.printerpix.co.uk/photo-gifts-for-grandparents-photo-blanket/","https://www.printerpix.co.uk/mink-personalised-blanket/",
        "https://www.printerpix.co.uk/cpg/custom-collage-canvas/","https://www.printerpix.co.uk/gifts-for-men-photo-blanket/","https://www.printerpix.co.uk/family-gifts-photo-blanket/",
        "https://www.printerpix.co.uk/cpg/photo-stone-slate/","https://www.printerpix.co.uk/cpg/photo-collage-canvas/","https://www.printerpix.co.uk/original-calendar-family/",
        "https://www.printerpix.co.uk/pocket-photobook-photo-cover/","https://www.printerpix.co.uk/printerpix-personalised-jigsaw-puzzle-mothers-day-photo-gifts/","https://www.printerpix.co.uk/printerpix-mother-and-son-photo-canvas-all-layout-sizes/",
        "https://www.printerpix.co.uk/personalised-photo-cushion/","https://www.printerpix.co.uk/printerpix-mother-and-son-photo-photobook/","https://www.printerpix.co.uk/cpg/personalised-birthday-book-your-photos/",
        "https://www.printerpix.co.uk/photo-tiles-prints/","https://www.printerpix.co.uk/big-and-large-canvas/"
        ]
    message = "<h1> Daily report - Mobile</h1>"
    bad_count_mobile = 0
    good_count_mobile = 0
    for link in links[:10]:
        temp,performance = getemailmessage(API_KEY,link,"mobile")
        if performance == 'passed':
            good_count_mobile+=1
        else: bad_count_mobile+=1
        print ("successfully load information for" + link)
        message = message + temp
    pass_rate_mobile = good_count_mobile/ (good_count_mobile+bad_count_mobile)
    message = message + '<p> Pass rate for mobile is ' + str(pass_rate_mobile)
    message = message + '<h1> Daily report - Desktop</h1>'
    bad_count_desktop = 0
    good_count_desktop = 0
    for link in links[:10]:
        temp,performance = getemailmessage(API_KEY,link,"desktop")
        if performance == 'passed':
            good_count_desktop+=1
        else: bad_count_desktop+=1
        print ("successfully load information for" + link)
        message = message + temp
    pass_rate_desktop = good_count_desktop / (good_count_desktop + bad_count_desktop)
    message = message + '<p> Pass rate for desktop is ' + str(pass_rate_desktop)

    subject = "Page Speed Report " + today
    msg = MIMEMultipart()
    password = 'Kah93613'
    msg['From'] = "shijun.ma@printerpix.co.uk"
    recipients = "shijun.ma@printerpix.co.uk,daniel.vasilescu@printerpix.co.uk,printerpix@360-om.co.uk"
    # msg['To'] = "shijun.ma@printerpix.co.uk"
    
    #Here we set the message. If we send an HTML we can include tags
    msg['Subject'] = subject
    message = message
    
    #It attaches the message and its format, in this case, HTML

    msg.attach(MIMEText(message, 'html'))
    
    #It creates the server instance from where the email is sent
    server = smtplib.SMTP("smtp-mail.outlook.com",587)
    server.starttls()
    
    #Login Credentials for sending the mail
    server.login('shijun.ma@printerpix.co.uk', password)
    
    #  recipients.split(',')
    # send the message via the server.
    server.sendmail(msg['From'],recipients.split(','), msg.as_string())
    server.quit()
    print(base64.b64decode(cloud_event.data["message"]["data"]))
