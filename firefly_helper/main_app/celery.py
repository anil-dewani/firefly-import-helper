import os
from celery import Celery, shared_task
from celery import Task
from celery import signals
import psutil
import time
import csv
import datetime
import pdfplumber
import subprocess
import json
from dateutil.parser import parse
from selenium import webdriver
import socket
import requests

webdriver_capabilities = {
    "browserName": "chrome",
    "browserVersion": "106.0",
    "selenoid:options": {
        "enableVNC": False,
        "enableVideo": True,
    },
}


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firefly_helper.settings.production')

app = Celery('firefly_worker')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

print(psutil.Process(os.getpid()).cmdline())


if any("celery" in s for s in psutil.Process(os.getpid()).cmdline()):
    import django; django.setup()
    from django.core.files.base import File
    from django.utils.text import slugify
    from main_app import models
    print("woah")

class identdict(dict):
    def __missing__(self, key):
        return key

class LogErrorsTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        super(LogErrorsTask, self).on_success(retval, task_id, args, kwargs)

@app.task(base=LogErrorsTask)
def log_message(message_type, message, statement_id):
    # making a new change
    statement_file = models.StatementFile.objects.get(id=statement_id)
    log_object = models.ProcessLog(
        mode=message_type,
        message=message,
    )
    log_object.save()
    statement_file.log_data.add(log_object)
    statement_file.save()

@app.task(base=LogErrorsTask)
def log_message_amazon(message_type, message, statement_id):
    statement_file = models.AmazonStatementFile.objects.get(id=statement_id)
    log_object = models.ProcessLog(
        mode=message_type,
        message=message,
    )
    log_object.save()
    statement_file.log_data.add(log_object)
    statement_file.save()

@app.task(base=LogErrorsTask)
def process_amazon_statement(statement_id):
    log_message_amazon.apply_async(("INFO","Started Amazon Statement Processing", statement_id))
    statement_file = models.AmazonStatementFile.objects.get(id=statement_id)
    if statement_file.status == "Processing":
        log_message_amazon.apply_async(("INFO","Extraction mode is amazon",statement_id))
        with open(statement_file.statement_file.path) as f:
            csv_reader = csv.reader(f)
            for line_no, line in enumerate(csv_reader, 1):
                if line_no == 1:
                    continue
                else:
                    try:
                        amazon_order_object = models.AmazonOrderDetail(
                            order_date = datetime.datetime.strptime(str(line[0]), "%Y-%m-%d").date(),
                            order_id = line[5],
                            product_title = line[2],
                            product_link = line[4],
                            order_amount = float(line[3].replace('Rs.','').replace(',','').replace(' ','')),
                            statement_file = statement_file,
                        )
                        amazon_order_object.save()
                    except Exception as e:
                        log_message_amazon.apply_async(("ERROR",str(e),statement_id))

        statement_file.status = "Processing"
        statement_file.save()

        scrape_additional_amazon_data.apply_async((statement_id,))
        return "Processed"
    else:
        return "Invalid Status Received"

@app.task(base=LogErrorsTask)
def scrape_additional_amazon_data(statement_id):
    log_message_amazon.apply_async(("INFO","Started Amazon Statement Processing", statement_id))
    statement_file = models.AmazonStatementFile.objects.get(id=statement_id)
    amazon_orders = models.AmazonOrderDetail.objects.filter(statement_file=statement_file).filter(status="Unprocessed")
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    internal_ips = [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
    selenoid_hosts = ["localhost","selenoid",hostname,str(internal_ips[0])]
    print("Trying to find selenoid hub : "+str(selenoid_hosts))
    approved_selenoid_url = None
    for selenoid_host in selenoid_hosts:
        print("trying :: "+selenoid_host)
        selenoid_hub_url = "http://"+selenoid_host+":4445/wd/hub"
        try:
            response = requests.get(selenoid_hub_url)
            if response.ok:
                approved_selenoid_url = selenoid_hub_url
                break
            else:
                approved_selenoid_url = None
                print(selenoid_host + " :: not approved")
        except:
            print(selenoid_host+" :: try/catch")
    
    print("selenoid url : "+str(approved_selenoid_url))
    if approved_selenoid_url:
        browser = webdriver.Remote(command_executor=approved_selenoid_url,desired_capabilities=webdriver_capabilities)
        
        for amazon_order in amazon_orders:
            amazon_url = amazon_order.product_link
            
            try:
                browser.get(amazon_url)
                time.sleep(5)
                main_category_text = browser.find_element('xpath','//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[1]/span/a').text
                category_list_text = browser.find_element('xpath','//*[@id="wayfinding-breadcrumbs_feature_div"]/ul').text
            except:
                main_category_text = ""
                category_list_text = ""
            
            amazon_order.main_category = main_category_text
            amazon_order.category_list = category_list_text
            log_message_amazon.apply_async(("INFO","Got Info: "+str(main_category_text)+">>"+str(category_list_text), statement_id))
            amazon_order.status = "Processed"
            amazon_order.save()

        statement_file.selenoid_session_id = str(browser.session_id)
        statement_file.status = "Processed"
        statement_file.save()
        browser.quit()
    else:
        return "No Selenoid Approved URLs formed"



@app.task(base=LogErrorsTask)
def convert_statement_file(statement_id):
    log_message.apply_async(("INFO","Started Processing File",statement_id))

    statement_file = models.StatementFile.objects.filter(id=statement_id).first()
    if statement_file.status == "Processing":
        if statement_file.statement_type == "Axis CC":
            log_message.apply_async(("INFO","Extraction mode is Axis CC",statement_id))
            statement_lines = []
            statement_pdf = pdfplumber.open(statement_file.statement_file.path)
            for statement_page in statement_pdf.pages:
                statement_table_data = statement_page.extract_table()
                if statement_table_data is not None:
                    for table_line in statement_table_data:
                        if table_line:
                            statement_lines.append(table_line)

            transaction_lines = []
            transaction_logging = False
            for statement_line in statement_lines:
                if statement_line:
                    if statement_line[0] == "DATE":
                        transaction_logging = True
                        continue
                    
                    if "End of Statement" in statement_line[0]:
                        transaction_logging = False
                    
                    if transaction_logging:
                        transaction_lines.append(statement_line)
                        log_message.apply_async(("INFO",statement_line,statement_id))


            for transaction_line in transaction_lines:      
                try:
                    # check if first column is an date
                    if parse(transaction_line[0], fuzzy=False):
                        if "Dr" in transaction_line[8].strip():
                            # its a debit entry
                            models.TransactionData(
                                transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d/%m/%Y").date(),
                                asset_account = "Axis CC",
                                amount_debit = float(transaction_line[8].strip().replace('Dr','').replace(',','').replace(' ','')),
                                description = str(transaction_line[2]).strip(),
                                statement_file = statement_file,
                                tags = "statement-id-"+str(statement_id),
                                status = 'Processed',
                            ).save()
                        elif "Cr" in transaction_line[8].strip():
                            # its a credit entry
                            models.TransactionData(
                                transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d/%m/%Y").date(),
                                asset_account = "Axis CC",
                                amount_credit = float(transaction_line[8].strip().replace('Cr','').replace(',','').replace(' ','')),
                                description = str(transaction_line[2]).strip(),
                                statement_file = statement_file,
                                tags = "statement-id-"+str(statement_id),
                                status = 'Processed',
                            ).save()
                        else:
                            log_message.apply_async(("ERROR","Transaction has no debit or credit amount somehow "+str(transaction_line[8]),statement_id))
                    
                except Exception as e:
                    log_message.apply_async(("ERROR",str(e),statement_id))


            log_message.apply_async(("INFO","Universal CSV File Mapped",statement_id))
            generate_csv_file.apply_async((statement_id,))
            return "Generating CSV"
        elif statement_file.statement_type == "Axis Savings":
            log_message.apply_async(("INFO","Extraction mode is Axis Savings",statement_id))
            statement_lines = list(csv.reader(open(statement_file.statement_file.path)))
            transaction_lines = []
            transaction_logging = False
            for statement_line in statement_lines:
                if statement_line:
                    # detecting start of transactions and end of transactions
                    if statement_line[0] == "Tran Date":
                        transaction_logging = True
                        continue

                    if "Charge Statement of Axis Account" in statement_line[0]:
                        transaction_logging = False

                    if transaction_logging:
                        transaction_lines.append(statement_line)
                        log_message.apply_async(("INFO",statement_line,statement_id))

            
            for transaction_line in transaction_lines:      
                try:
                    if transaction_line[3].strip():
                        # its a debit entry
                        models.TransactionData(
                            transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d-%m-%Y").date(),
                            asset_account = "Axis Savings",
                            amount_debit = float(transaction_line[3].strip().replace(',','').replace(' ','')),
                            description = str(transaction_line[2]).strip(),
                            statement_file = statement_file,
                            tags = "statement-id-"+str(statement_id),
                            status = 'Processed',
                        ).save()
                    elif transaction_line[4].strip():
                        # its a credit entry
                        models.TransactionData(
                            transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d-%m-%Y").date(),
                            asset_account = "Axis Savings",
                            amount_credit = float(str(transaction_line[4].replace(' ',''))),
                            description = str(transaction_line[2]).strip(),
                            statement_file = statement_file,
                            tags = "statement-id-"+str(statement_id),
                            status = 'Processed',
                        ).save()
                    else:
                        log_message.apply_async(("ERROR","Transaction has no debit or credit amount somehow",statement_id))
                    
                except Exception as e:
                    log_message.apply_async(("ERROR",str(e),statement_id))

            log_message.apply_async(("INFO","Universal CSV File Mapped",statement_id))
            generate_csv_file.apply_async((statement_id,))
            return "Generating CSV"
        elif statement_file.statement_type == "ICICI CC":
            log_message.apply_async(("INFO","Extraction mode is ICICI CC",statement_id))
            statement_lines = list(csv.reader(open(statement_file.statement_file.path)))
            transaction_lines = []
            transaction_logging = False
            for statement_line in statement_lines:
                if statement_line:
                    # detecting start of transactions and end of transactions
                    if statement_line[0] == "Date":
                        transaction_logging = True
                        continue

                    if "EMI Details" in statement_line[0]:
                        transaction_logging = False

                    if transaction_logging:
                        transaction_lines.append(statement_line)
                        log_message.apply_async(("INFO",statement_line,statement_id))

            
            for transaction_line in transaction_lines:      
                try:
                    # check if first column is an date
                    if parse(transaction_line[0], fuzzy=False):
                        if "CR" in transaction_line[6].strip():
                            # its a credit entry
                            models.TransactionData(
                                transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d/%m/%Y").date(),
                                asset_account = "ICICI CC",
                                amount_credit = float(transaction_line[5].strip().replace(',','').replace(' ','')),
                                description = str(transaction_line[2]).strip(),
                                statement_file = statement_file,
                                tags = "statement-id-"+str(statement_id),
                                status = 'Processed',
                            ).save()
                        elif transaction_line[6].strip() == '':
                            # its a debit entry
                            models.TransactionData(
                                transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d/%m/%Y").date(),
                                asset_account = "ICICI CC",
                                amount_debit = float(transaction_line[5].strip().replace(',','').replace(' ','')),
                                description = str(transaction_line[2]).strip(),
                                statement_file = statement_file,
                                tags = "statement-id-"+str(statement_id),
                                status = 'Processed',
                            ).save()
                        else:
                            log_message.apply_async(("ERROR","Transaction has no debit or credit amount somehow",statement_id))
                    
                except Exception as e:
                    log_message.apply_async(("ERROR",str(e),statement_id))
            log_message.apply_async(("INFO","Universal CSV File Mapped",statement_id))
            generate_csv_file.apply_async((statement_id,))
            return "Generating CSV"
        elif statement_file.statement_type == "ICICI Savings":
            log_message.apply_async(("INFO","Extraction mode is ICICI Savings",statement_id))
            statement_lines = list(csv.reader(open(statement_file.statement_file.path)))
            transaction_lines = []
            transaction_logging = False
            for statement_line in statement_lines:
                if statement_line:
                    # detecting start of transactions and end of transactions
                    if statement_line[0] == "DATE":
                        transaction_logging = True
                        continue

                    if "Summary of TDS/Interest" in statement_line[0]:
                        transaction_logging = False

                    if transaction_logging:
                        transaction_lines.append(statement_line)
                        log_message.apply_async(("INFO",statement_line,statement_id))

            
            for transaction_line in transaction_lines:      
                try:
                    if transaction_line[4].strip() and float(transaction_line[4].replace(',','').replace(' ','')) > 0:
                        # its a debit entry
                        models.TransactionData(
                            transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d-%m-%Y").date(),
                            asset_account = "ICICI Savings",
                            amount_debit = float(transaction_line[4].strip().replace(',','').replace(' ','')),
                            description = str(transaction_line[2]).strip(),
                            statement_file = statement_file,
                            tags = "statement-id-"+str(statement_id),
                            status = 'Processed',
                        ).save()
                    elif transaction_line[3].strip() and float(transaction_line[3].replace(',','').replace(' ','')) > 0:
                        # its a credit entry
                        models.TransactionData(
                            transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d-%m-%Y").date(),
                            asset_account = "ICICI Savings",
                            amount_credit = float(str(transaction_line[3].replace(' ',''))),
                            description = str(transaction_line[2]).strip(),
                            statement_file = statement_file,
                            tags = "statement-id-"+str(statement_id),
                            status = 'Processed',
                        ).save()
                    else:
                        log_message.apply_async(("ERROR","Transaction has no debit or credit amount somehow",statement_id))
                    
                except Exception as e:
                    log_message.apply_async(("ERROR",str(e),statement_id))
            log_message.apply_async(("INFO","Universal CSV File Mapped",statement_id))
            generate_csv_file.apply_async((statement_id,))
            return "Generating CSV"
        elif statement_file.statement_type == "SBI CC":
            log_message.apply_async(("INFO","Extraction mode is SBI CC",statement_id))
            time.sleep(15)
            log_message.apply_async(("INFO","Universal CSV File Mapped",statement_id))
            generate_csv_file.apply_async((statement_id,))
            return "Generating CSV"
        elif statement_file.statement_type == "SBI Savings":
            log_message.apply_async(("INFO","Extraction mode is SBI Savings",statement_id))
            statement_lines = list(csv.reader(open(statement_file.statement_file.path),delimiter='\t'))
            transaction_lines = []
            transaction_logging = False
            for statement_line in statement_lines:
                if statement_line:
                    # detecting start of transactions and end of transactions
                    if statement_line[0] == "Txn Date":
                        transaction_logging = True
                        continue

                    if "This is a computer generated" in statement_line[0]:
                        transaction_logging = False

                    if transaction_logging:
                        transaction_lines.append(statement_line)
                        log_message.apply_async(("INFO",statement_line,statement_id))

            
            for transaction_line in transaction_lines:      
                try:
                    # check if first column is an date
                    if parse(transaction_line[0], fuzzy=False):
                        if transaction_line[5].strip():
                            # its a debit entry
                            models.TransactionData(
                                transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d %b %Y").date(),
                                asset_account = "SBI Savings",
                                amount_debit = float(transaction_line[5].strip().replace(',','').replace(' ','')),
                                description = str(transaction_line[2]).strip(),
                                statement_file = statement_file,
                                tags = "statement-id-"+str(statement_id),
                                status = 'Processed',
                            ).save()
                        elif transaction_line[6].strip():
                            # its a credit entry
                            models.TransactionData(
                                transaction_date = datetime.datetime.strptime(str(transaction_line[0]).strip(), "%d %b %Y").date(),
                                asset_account = "SBI Savings",
                                amount_credit = float(transaction_line[6].strip().replace(',','').replace(' ','')),
                                description = str(transaction_line[2]).strip(),
                                statement_file = statement_file,
                                tags = "statement-id-"+str(statement_id),
                                status = 'Processed',
                            ).save()
                        else:
                            log_message.apply_async(("ERROR","Transaction has no debit or credit amount somehow",statement_id))
                    
                except Exception as e:
                    log_message.apply_async(("ERROR",str(e),statement_id))
            log_message.apply_async(("INFO","Universal CSV File Mapped",statement_id))
            generate_csv_file.apply_async((statement_id,))
            return "Generating CSV"
        else:
            return "Invalid Statement Type"

@app.task(base=LogErrorsTask)
def process_amazon_transaction(statement_id, transaction_id):
    """
    TODO: Try to map transaction to amazon order details
    TODO: if match is found, get data from dataforseo
    TODO: update transaction data with relevant extra information
    """
    statement_file = models.StatementFile.objects.get(id=statement_id)
    transaction_object = models.TransactionData.objects.get(id=transaction_id)
    if transaction_object.amount_debit:
        if models.AmazonOrderDetail.objects.filter(order_date__date=transaction_object.transaction_date).filter(order_amount=transaction_object.amount_debit).count() > 0:
            log_message.apply_async(("INFO","Amazon Debit Transaction Mapped",statement_id))
            detected_amazon_order = models.AmazonOrderDetail.objects.filter(order_date__date=transaction_object.transaction_date).filter(order_amount=transaction_object.amount_debit).first()
            transaction_object.notes = detected_amazon_order.product_title + " " + detected_amazon_order.product_link
            transaction_object.category = detected_amazon_order.main_category
            transaction_object.tags = detected_amazon_order.category_list
            transaction_object.save()
    else:
        if models.AmazonOrderDetail.objects.filter(order_date__date=transaction_object.transaction_date).filter(order_amount=transaction_object.amount_credit).count() > 0:
            log_message.apply_async(("INFO","Amazon Credit Transaction Mapped",statement_id))
            detected_amazon_order = models.AmazonOrderDetail.objects.filter(order_date__date=transaction_object.transaction_date).filter(order_amount=transaction_object.amount_credit).first()
            transaction_object.notes = detected_amazon_order.product_title + " " + detected_amazon_order.product_link
            transaction_object.category = detected_amazon_order.main_category
            transaction_object.tags = detected_amazon_order.category_list
            transaction_object.save()
    
    transaction_object.status = 'Processed'
    transaction_object.save()

@app.task(base=LogErrorsTask)
def generate_csv_file(statement_id):
    time.sleep(2)
    statement_file = models.StatementFile.objects.get(id=statement_id)
    transactions = models.TransactionData.objects.filter(statement_file=statement_file)
    
    # checking if all transactions are set to 'Processed', if not wait for 10minutes
    attempts = 0
    while True:
        if transactions.count() == transactions.filter(status='Processed').count():
            log_message.apply_async(("INFO","All Transactions Processed : "+str(transactions.count()),statement_id))
            break
        else:
            attempts += 1
            log_message.apply_async(("WARNING","Waiting for transactions. Attempt: "+str(attempts),statement_id))
            time.sleep(10)
            if attempts > 60:
                log_message.apply_async(("ERROR","Timeout processing transactions. Attempt: "+str(attempts),statement_id))
                return "Timeout of 10 minutes Reached"


    
    qs = transactions
    output_file_name = slugify(statement_file.statement_type)+"-"+slugify(str(statement_file.created_at))+".csv"
    outfile_path = "/tmp/"+output_file_name
    log_message.apply_async(("INFO","CSV File Created: "+str(outfile_path),statement_id))
    model = qs.model
    file_object = open(outfile_path,'a+')
    writer = csv.writer(file_object)	
    headers = []
    for field in model._meta.fields:
        headers.append(field.name)
    writer.writerow(headers)
	
    for obj in qs:
        row = []
        for field in headers:
            val = getattr(obj, field)
            if callable(val):
                val = val()
            row.append(val)
        writer.writerow(row)
    log_message.apply_async(("INFO","CSV Data Ready",statement_id))
    time.sleep(3)
    statement_file.processed_file.save(output_file_name, File(file_object))
    statement_file.save()
    time.sleep(3)
    statement_file.status = "Processed"
    statement_file.save()
    log_message.apply_async(("DEBUG",str(statement_file.status),statement_id))
    log_message.apply_async(("DEBUG",str(file_object),statement_id))
    log_message.apply_async(("INFO","CSV File Ready For Download",statement_id))
    return "CSV File Created"
