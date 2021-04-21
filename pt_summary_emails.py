import win32com.client
from win32com.client import Dispatch, constants
import emailtemplates as et
import pandas as pd
import time
import os
import numpy as np

def send_email(emails, emailbody, agency, code, attachment):
    recipient = emails
    const=win32com.client.constants
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = "Data Request: 2018 Summary of Public Transportation--{}".format(agency)
    newMail.BodyFormat = 2
    newMail.HTMLBody = emailbody.format(code)
    newMail.Attachments.Add(Source=attachment)
    newMail.To = recipient
    newMail.SentOnBehalfOfName =
    newMail.Send()


def send_email_ferry(emails, emailbody, agency, attachment, collector):
    recipient = emails
    const=win32com.client.constants
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = "Data Request: 2018 Summary of Public Transportation--{}".format(agency)
    newMail.BodyFormat = 2
    newMail.HTMLBody = emailbody
    newMail.Attachments.Add(Source = collector)
    newMail.Attachments.Add(Source=attachment)
    newMail.To = recipient
    newMail.SentOnBehalfOfName =
    newMail.Send()
def send_email_cp(emails, emailbody, agency, attachment):
    recipient = emails
    const=win32com.client.constants
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = "Data Request: 2018 Summary of Public Transportation--{}".format(agency)
    newMail.BodyFormat = 2
    newMail.HTMLBody = emailbody
    newMail.Attachments.Add(Source=attachment)
    newMail.To = recipient
    newMail.SentOnBehalfOfName =
    newMail.Send()

df = pd.read_excel(r'I:\Public_Transportation\Data_Team\PT_Summary\2018\email_list.xlsx')
for index, row in df.iterrows():
    time.sleep(2)
    if row['org_type'] == 'tribe':
        emailbody = et.pt_summary_tribe_data_request
        send_email(row['email'], emailbody, row['org_name'], row['code'], row['coversheet_path'])
    elif row['org_type'] == 'transit':
        emailbody = et.pt_summary_ptrs_data_request
        send_email(row['email'], emailbody, row['org_name'], row['code'], row['coversheet_path'])
    elif row['org_type'] == 'ferry':
        emailbody = et.pt_summary_ferries_data_request
        send_email_ferry(row['email'], emailbody, row['org_name'],row['coversheet_path'], row['collector_path'])
    elif row['org_type'] == 'cp':
        emailbody = et.pt_summary_cp_data_request
        send_email_cp(row['email'], emailbody, row['org_name'],row['coversheet_path'])





