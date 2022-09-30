from django.shortcuts import render, redirect
from main_app import models
from main_app import forms
from main_app import celery
from django.contrib import messages



# Create your views here.
def index(request):
    
    context = {
        'title': 'Firefly Import Helper',
    }

    template = 'home.html'
    return render(request, template, context)


def process_uploaded_files(request, file_ids):
    uploaded_files = models.StatementFile.objects.filter(id__in=file_ids.split('-'))

    context = {
        'title': 'Process Files',
        'uploaded_files': uploaded_files,
        'file_ids': file_ids,
    }
    template = 'process.html'
    return render(request, template, context)

def processing_uploaded_files(request, file_ids):
    uploaded_files = models.StatementFile.objects.filter(id__in=file_ids.split('-'))

    for uploaded_file in uploaded_files:
        if uploaded_file.status == "Unprocessed":
            uploaded_file.status = "Processing"
            celery.convert_statement_file.apply_async((uploaded_file.id,))

    context = {
        'title': 'Processing Files',
        'uploaded_files': uploaded_files,
        'file_ids': file_ids,
    }
    template = 'processing.html'
    return render(request, template, context)


def cancel_uploaded_files(request, file_ids):
    uploaded_files = models.StatementFile.objects.filter(id__in=file_ids.split('-'))
    
    for uploaded_file in uploaded_files:
        uploaded_file.status = 'Cancelled'
        uploaded_file.save()
    messages.add_message(request, messages.INFO, 'All Uploaded Files Cancelled')

    return redirect('index')


def process_logs(request, file_id):
    uploaded_file = models.StatementFile.objects.filter(id=file_id).first()
    
    context = {
        'title': 'Process Log Entries',
        'log_data': uploaded_file.logs,
    }
    template = 'logs.html'
    return render(request, template, context)


def upload_statements(request, category):
    if category == "axis-cc":
        statement_type = "Axis CC"
    elif category == "axis-savings":
        statement_type = "Axis Savings"
    elif category == "icici-cc":
        statement_type = "ICICI CC"
    elif category == "icici-savings":
        statement_type = "ICICI Savings"
    elif category == "sbi-cc":
        statement_type = "SBI CC"
    elif category == "sbi-savings":
        statement_type = "SBI Savings"
    else:
        statement_type = None
    
    if request.method == 'POST':
        form = forms.StatementFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        if form.is_valid():
            instance_ids = ""
            for f in files:
                file_instance = models.StatementFile(files=f)
                file_instance.statement_type = statement_type
                file_instance.save()
                instance_ids = instance_ids + str(file_instance.id) + "-"
            instance_ids = instance_ids[:-1]
            return redirect('process_uploaded_files',instance_ids)
    else:
        form = forms.StatementFileForm()

    context = {
        'title': statement_type+' Importer',
        'form': form,
    }

    template = 'upload.html'
    return render(request, template, context)



def faq_section(request):
    context = {
        'title': 'Importer FAQ',
    }
    template = 'faq.html'
    return render(request, template, context)