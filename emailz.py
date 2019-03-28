import win32com.client
from win32com.client import Dispatch, constants
import emailtemplates as et
import pandas as pd
import time
import os

df = pd.read_excel(r'G:\Evaluation Group\National Transit Database\2018 NTD\ntd contacts list updated.xlsx')
ls = df.System.tolist()
org_path = r'G:\Evaluation Group\National Transit Database\2018 NTD\Pre-populated Excel Files'
attachment_column = []
for i in ls:
    dir_path = org_path + '\\' + i
    other_ls = os.listdir(dir_path)
    try:
        attachment_column.append(attachment_list)
    except NameError:
        pass
    attachment_list = []
    for file in other_ls:
        file_path = dir_path + '\\' +file
        attachment_list.append((file_path))

attachment_column.append(attachment_list)
df['Attachments'] = attachment_column
type_of_email = []
for i in df.Attachments:
    if len(i) == 3:
        type_of_email.append('5311_only')
    else:
        type_of_email.append('reduced_reporter')
df['type_of_email'] = type_of_email


def send_email(emails, attachmentpath, agency, name, emailbody):
    recipient = emails
    const=win32com.client.constants
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = "2018 NTD Reporting - {}".format(agency)
    newMail.BodyFormat = 2
    emailbody = emailbody.format(name)
    newMail.HTMLBody = emailbody
    newMail.To = recipient
    for attachment in attachmentpath:
        newMail.Attachments.Add(Source = attachment)
    newMail.SentOnBehalfOfName = 'NTD@wsdot.wa.gov'
    newMail.Send()

emailbody = et.ntd_email_reduced_reporters
count = 0
for index, row in df.iterrows():
    if row['type_of_email'] == 'reduced_reporter':
        emailbody = et.ntd_email_reduced_reporters
    elif row['type_of_email'] == '5311_only':
        emailbody = et.ntd_email_5311_reporters
    send_email(row['Email'], row['Attachments'], row['System'], row['FirstName'], emailbody)
    time.sleep(3)




