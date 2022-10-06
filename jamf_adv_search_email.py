import requests
import os
import argparse
import getpass
import sys
import smtplib
import boto3
import json

jamfURL = "https://jamf.corp.example.com:8443"
advSearchAPICall = "/JSSResource/advancedcomputersearches/name/"

emailList = ['you@example.com']
emailServer = 'mail.example.com'
smtpPort = 25
awsSecretId = 'Jamf-Computer-Report-API'
awsRegion = 'us-west-2'
awsSecretUserKey = 'username'
awsSecretPassKey = 'password'

def create_parser():
    parser = argparse.ArgumentParser(description="This tool is used to pull jamf advanced searches into reports and email them.")
    parser.add_argument('--advsearch', type=str, required=True, help="(Required) Provide the name of the advance search you wish to pull reports from.")
    parser.add_argument('--jamfurl', type=str, required=False, help="Runs with a custom jamf url of your choice. Sepcfiy the jamf base url and port e.g: https:jamf.example.com:8443")
    parser.add_argument('--nosslverify', required=False, action='store_true', help="Disables SSL checking")
    parser.add_argument('--prompt', '-p',  required=False, action='store_true',help="Prompts for username and password instead of using enviroment variable.")
    return parser


parser = create_parser()
args = parser.parse_args()


if args.nosslverify == True:
    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    ssl_verification = False
else:
    ssl_verification = True


def sendReport(reportName, computerArray, reportReceivers):
    emailbody= "\n".join(computerArray)
    message = "From: Jamf-Reporting <Jamf-Reporting@Jamf.example.com>\n" +"Subject: " + reportName + "\n" + reportName +" Jamf Report\n-----------\n" + emailbody
    sender="Jamf-Reports@example.com"
    recipients = reportReceivers

    try:
        smtplib.SMTP(emailServer, smtpPort).sendmail(sender, recipients, message)
        print("Sent Email")
    except SMTPException:
        print("Error: Unable to send email.")
        sys.exit()


def collect_aws_secret(sid, region, usernamekey, passwordkey):
    global username
    global password
    try:
        client = boto3.client('secretsmanager', region_name=region)
        s = client.get_secret_value(SecretId=sid)['SecretString']
        jsonsecret = json.loads(s)
        username = jsonsecret[usernamekey]
        password = jsonsecret[passwordkey]
        print("Secret Collected.")
    except:
        print("Unable to locate AWS secret. Verify your secret information is correct or prompt for creds using --prompt")
        sys.exit()


def prompt_for_creds():
    global username
    global password
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")


if args.jamfurl:
    jamfURL = args.jamfurl

print('Jamf URL: ', jamfURL)
print('Jamf Adv Search: ', args.advsearch)

try:
    req = requests.get(jamfURL, verify=ssl_verification)
except requests.exceptions.SSLError:
    print("The site returned an SSL error. Verifiy your url is correct. If needed pass in a --nosslverify flag to skip ssl verification. This will reduce security.")
    sys.exit()
except:
    print("A connection error occurred. Make sure you have the correct URL and port if needed.")
    sys.exit()
else:
    print(f"Sucessfully connected to site with status code {req.status_code}")
    print("Attemping to collect credentials")
    if args.prompt:
        prompt_for_creds()
    else:
        collect_aws_secret(awsSecretId, awsRegion, awsSecretUserKey, awsSecretPassKey)



try:
    req = requests.get(jamfURL + advSearchAPICall + args.advsearch, verify=ssl_verification, auth=(username, password), headers={"accept":"application/json"})
    if req.status_code == 401:
        print("Authentication failed. Please try again.")
        sys.exit()
except:
    print("A connection error occurred.")
    sys.exit()
else:
    data = req.json()
    computerArray = [f"Computer Name: {computer['Computer_Name']} | Last Check In: {computer['Last_Check_in']} | Username: {computer['Username']}" for computer in data['advanced_computer_search']['computers']]
    sendReport(args.advsearch, computerArray, emailList)
