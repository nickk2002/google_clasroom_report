from __future__ import print_function
import pickle
import os.path
import time
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest

SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly','https://www.googleapis.com/auth/classroom.rosters',"https://www.googleapis.com/auth/classroom.profile.emails","https://www.googleapis.com/auth/classroom.push-notifications"]



def list_courses(response, exception):
    if exception is None:
        return response['courses']

def get_all_courses(service):
    batch1 = service.new_batch_http_request()
    nextpageToken = ""
    list_id = []
    while nextpageToken is not None:

        result = service.courses().list(
            pageSize=500,
            pageToken=nextpageToken,
            fields="nextPageToken,courses(id)"
        ).execute()
        lista_curs = result['courses']

        for curs in lista_curs:
            list_id.append(curs.get('id'))
        nextpageToken = result.get("nextPageToken")
    print("Ther are :" + str(len(list_id)))
    return list_id

def itereate_students(service):
    list_id = get_all_courses(service)
    list_fara_email = []
    max_limit = 200000
    counter = 0
    for curs_id in list_id:
        if counter > max_limit:
            return
        counter += 1
        next_page_token = ""
        elevi_clasa = 0
        while next_page_token is not None:
            lista_studenti = service.courses().students().list(
                courseId=curs_id,
                pageToken=next_page_token,
                fields="nextPageToken,students(userId,profile/emailAddress)"
            ).execute()

            next_page_token = lista_studenti.get("nextPageToken")
            lista_studenti = lista_studenti.get("students")

            if lista_studenti is None:
                break
            elevi_clasa += len(lista_studenti)
            for student in lista_studenti:
                separator = "/"
                student_id = student.get("userId")
                email = student.get("profile").get("emailAddress")
                if email is None:
                    list_fara_email.append(student_id)
                    # daca nu are email atunci numai continui cu studentul
                    continue
                try:
                    print(curs_id, student_id, email, sep = separator)
                except:
                    print("eroare la cursul : ",curs_id,student_id, sep=separator)
                    continue
        print(curs_id,elevi_clasa)
    if len(list_fara_email) > 0:
        print("Studentii fara email (adica care ar trebui stersi sunt aici : ", list_fara_email)

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('classroom', 'v1', credentials=creds)



    timp_initial = time.time()
    file = open("ids",'w')
    sys.stdout = file
    itereate_students(service)
    get_all_courses(service)
    print(time.time() - timp_initial,'s')

if __name__ == '__main__':
    main()