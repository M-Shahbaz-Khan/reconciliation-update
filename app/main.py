from flask import Flask, request
import logging
import sys
import pandas as pd
import os
import numpy as np
import traceback
import threading
from airtable import Airtable
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from app.import_config.airtable_data import data
from datetime import datetime
from pytz import timezone
import pytz

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
GLOW_SCRIPT_PATH = './app/glowscripts/'
AIRTABLE_CREDS = os.getenv('airtable_credentials')

def remove_fields(df):
    df.columns = list(map(lambda x: str.replace(x, 'fields.', ''), df.columns.values))
    return df

def get_gsheet_creds():
    creds = None
    if os.path.exists(GLOW_SCRIPT_PATH + 'token.json'):
        creds = Credentials.from_authorized_user_file(GLOW_SCRIPT_PATH + 'token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # Refresh credentials locally
        # else:
        #     flow = InstalledAppFlow.from_client_secrets_file(
        #         GLOW_SCRIPT_PATH + 'gsheet_credentials.json', SCOPES)
        #     creds = flow.run_local_server(port=0)
        with open(GLOW_SCRIPT_PATH + 'token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

def upload_data(range_name, spreadsheet, data, service):
    range = range_name
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet, range=range, body={})
    response = request.execute()
    values = data.values.tolist()
    values.insert(0, data.columns.values.tolist())
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet, range=range,
        valueInputOption='USER_ENTERED', body=body).execute()
    print(range + ': {0} cells updated.'.format(result.get('updatedCells')))

def process_general_tables(google_service, calling_sheet, formatted_date, status_range):
        try:
                airtable = Airtable('appvudnVFWtHNxmQQ', 'WC Policies', AIRTABLE_CREDS)
                ipfs_linking = pd.json_normalize(airtable.get_all(fields=['Id', 'IPFS Account']).copy()).apply(lambda x: x.apply(lambda y: ','.join([str(i) for i in y]) if type(y) == list else y), axis=1).fillna('')
                ipfs_linking = remove_fields(ipfs_linking[['id', 'createdTime', 'fields.Id', 'fields.IPFS Account']].copy())

                upload_data('IPFS_Linking!A:Z', calling_sheet, ipfs_linking, google_service)

                airtable = Airtable('appcWje2y5RZJY6PM', 'Acctg Bord', AIRTABLE_CREDS)
                ah_bord = pd.json_normalize(airtable.get_all(fields=['policy_number', 'wc_policy_text', 'policy_rec_id', 'Policy Effective Date (from WC Policies)', 'wc_policy_number', 'Net Remit', 'Status', 'Bord YearMonth']).copy()).apply(lambda x: x.apply(lambda y: ','.join([str(i) for i in y]) if type(y) == list else y), axis=1).fillna('')
                ah_bord = remove_fields(ah_bord)
                ah_bord = ah_bord[['id', 'policy_number', 'wc_policy_text', 'policy_rec_id', 'Policy Effective Date (from WC Policies)', 'wc_policy_number', 'Net Remit', 'Status', 'Bord YearMonth']].copy()

                upload_data('AH_Bord!A:Z', calling_sheet, ah_bord, google_service)

                airtable = Airtable('app9RJbzpT3jQFn1A', 'Reconciliation - Policies', AIRTABLE_CREDS)
                reconciliation_policies = pd.json_normalize(airtable.get_all(fields=['wc_policy_text [DND]', 'Reconciliation Status']).copy()).apply(lambda x: x.apply(lambda y: ','.join([str(i) for i in y]) if type(y) == list else y), axis=1).fillna('')
                reconciliation_policies = remove_fields(reconciliation_policies)
                reconciliation_policies = reconciliation_policies[['wc_policy_text [DND]', 'Reconciliation Status']].copy()

                upload_data('Data_Reconciliation_Policies!A:Z', calling_sheet, reconciliation_policies, google_service)
                tb = "No error"
        except Exception:
                print('\nError Processing General Tables')
                tb = traceback.format_exc()
                status = pd.DataFrame([{'Last Data Import Status' : 'Fail'}, {'Last Data Import Status' : formatted_date}])
                upload_data(status_range, calling_sheet, status, google_service)
                raise Exception
        else:
                tb = "No error"
        finally:
                print(tb)

def process_filtered_tables(table, policy_number, bureau_id, control_number, google_service, calling_sheet, formatted_date, status_range):
        try:
                airtable = Airtable(table['base'], table['airtable_name'], AIRTABLE_CREDS)
                
                if('filter_control_number' in table.keys()):
                        print(' Getting', table['sheet_name'], 'for', table['filter_pol_number'], 'and', table['filter_control_number'])
                        curr_table = airtable.get_all(formula="OR(FIND(" + policy_number + ", " + table['filter_pol_number'] + ")!=0 ,FIND(" + control_number + ", " + table['filter_control_number'] + ")!=0)")
                elif('filter_pol_number' in table.keys()):
                        print(' Getting', table['sheet_name'], 'for', table['filter_pol_number'])
                        curr_table = airtable.get_all(formula="{" + table['filter_pol_number'] + "}=" + "'" + policy_number + "'")
                elif('filter_bureau_id' in table.keys()):
                        print(' Getting', table['sheet_name'], 'for', table['filter_bureau_id'])
                        formula_string = "{" + table['filter_bureau_id'] + "}=" + "'" + bureau_id + "'"
                        curr_table = airtable.get_all(formula=formula_string)
                elif('view' in table.keys()):
                        print(' Getting', table['sheet_name'], 'for', table['view'])
                        curr_table = airtable.get_all(view=table['view'])
                else:
                        print(' Getting', table['sheet_name'], '(All)')
                        curr_table = airtable.get_all()

                curr_table = pd.json_normalize(curr_table.copy()).apply(lambda x: x.apply(lambda y: ','.join([str(i) for i in y]) if type(y) == list else y), axis=1).fillna('')

                cols = np.load(GLOW_SCRIPT_PATH + table['sheet_name'] + '.npy', allow_pickle=True)
                cols = ['fields.Contract ID' if ('fields.Chubb Contract ID' in x and 'WCS_' in table['sheet_name']) else x for x in cols]
                downloaded_cols = set(curr_table.columns.values)

                for col in cols:
                        if(col not in downloaded_cols):
                                curr_table[col] = ''

                if('rename' in table.keys()):
                        curr_table.rename(columns=table['rename'], inplace=True)

                if('copy' in table.keys()):
                        for k, v in table['copy'].items():
                                curr_table[v] = curr_table[k].copy()

                curr_table = curr_table[cols]
                curr_table.columns = list(map(lambda x: str.replace(x, 'fields.', ''), curr_table.columns.values))
                if 'createdTime' in curr_table.columns:
                        curr_table.loc[:, 'createdTime'] = pd.to_datetime(curr_table.createdTime).dt.strftime('%m/%d/%Y')
                curr_table.fillna('', inplace=True)

                range = table['sheet_name'] + '!A:BZ'
                request = google_service.spreadsheets().values().clear(spreadsheetId=calling_sheet, range=range, body={})
                request.execute() # Clear previous data
                values = curr_table.values.tolist()
                values.insert(0, curr_table.columns.values.tolist())
                body = {
                        'values': values
                }
                result = google_service.spreadsheets().values().update(
                spreadsheetId=calling_sheet, range=range,
                valueInputOption='USER_ENTERED', body=body).execute()

                print(range + ': {0} cells updated.'.format(result.get('updatedCells')))
                tb = "No error"
        except Exception:
                print('\nError Processing', table, policy_number, bureau_id, control_number, "|")
                tb = traceback.format_exc()
                status = pd.DataFrame([{'Last Data Import Status' : 'Fail'}, {'Last Data Import Status' : formatted_date}])
                upload_data(status_range, calling_sheet, status, google_service)
                raise Exception
        else:
                tb = "No error"
        finally:
                print(tb)

class MyWorker():
        def __init__(self, policy_number, bureau_id, control_number, calling_sheet, google_service, status_range, formatted_date):
                self.policy_number = policy_number
                self.bureau_id = bureau_id
                self.control_number = control_number
                self.calling_sheet = calling_sheet
                self.google_service = google_service
                self.status_range = status_range
                self.formatted_date = formatted_date
                thread = threading.Thread(target=self.run, args=())
                thread.daemon = True
                thread.start()

        def run(self):
                logging.info(f'run MyWorker {self.policy_number}')

                for table in data:
                        process_filtered_tables(table, self.policy_number, self.bureau_id, self.control_number, self.google_service, self.calling_sheet, self.formatted_date, self.status_range)

                status = pd.DataFrame([{'Last Data Import Status' : 'Success'}, {'Last Data Import Status' : self.formatted_date}])
                upload_data(self.status_range, self.calling_sheet, status, self.google_service)


@app.route("/", methods=["POST", "GET"])
def home_view():
        if request.form.get('pass') == os.getenv('password'):
                policy_number = str(request.form.get('policy_number'))
                bureau_id = str(request.form.get('bureau_id'))
                control_number = str(request.form.get('control_number'))
                calling_sheet = str(request.form.get('calling_sheet'))
                status_range = str(request.form.get('status_range'))

                date_format='%m/%d/%Y %H:%M:%S %Z'
                date = datetime.now(tz=pytz.utc)
                date = date.astimezone(timezone('US/Pacific'))
                formatted_date = date.strftime(date_format)

                creds = get_gsheet_creds()
                google_service = build('sheets', 'v4', credentials=creds)

                status = pd.DataFrame([{'Last Data Import Status' : 'In Progress'}, {'Last Data Import Status' : formatted_date}])
                upload_data(status_range, calling_sheet, status, google_service)

                process_general_tables(google_service, calling_sheet, formatted_date, status_range)
                MyWorker(policy_number, bureau_id, control_number, calling_sheet, google_service, status_range, formatted_date)
                return "Processed data for " + str(policy_number) + " and returning to " + str(calling_sheet)
        else:
                return "Access Denied"

@app.route("/test", methods=["POST", "GET"])
def hello_world():
        return "abcd"