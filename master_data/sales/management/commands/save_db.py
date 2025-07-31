import http.client
from django.core.management.base import BaseCommand
import pandas as pd
from sales.models import *
from master.models import *
from django.core.mail import EmailMessage
from datetime import datetime, time
from master_data.local_settings import settings_for_backup as sfb
import json
import sys
import zipfile
from django.conf import settings
from django.db import transaction
import time
import requests
import os
import subprocess
import logging
from pathlib import Path
from django.db.models import Q

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

folder_path = os.path.join(BASE_DIR, "media", "output")

if not os.path.exists(folder_path) :
    os.makedirs(os.path.join(BASE_DIR, "media", "output"))

log_file = os.path.join(BASE_DIR, "media", "output", "db_to_excel.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger().addHandler(logging.StreamHandler())


API_URL = "https://dev-bco.businesscorporateofficer.com/api/master-data-dokter/7"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Host': 'dev-bco.businesscorporateofficer.com'
}

def get_last_page(api_url):
    resp = requests.get(api_url)
    if resp.status_code == 200:
        return int(resp.json().get('data', {}).get('last_page', 1))
    raise ValueError("Gagal mendapatkan last_page dari API.")

def get_data_page(i):
    try:
        resp = requests.get(f"{API_URL}?page={i}", headers=HEADERS)
        if resp.status_code == 200 and 'application/json' in resp.headers.get('Content-Type', ''):
            return resp.json().get('data', {}).get('data', [])
        logging.warning(f"[WARN] Invalid response on page {i}: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[NETWORK ERROR] Page {i} gagal: {e}")
    return []

def process_doctor_not_found(g):
    return {
        'active': "Not Set",
        'accurate_code': g.get('kode_pelanggan_old'),
        'rayon_coverage_name': g.get('rayon_asal'),
        'dr_full_name': g.get('nama_dokter'),
        'apps_bco_id': g.get('id_dokter')
    }

def process_doctor_from_db(g):
    try:
        doctor = DoctorDetail.objects.using('sales').get(jamet_id=int(g.get('id_dokter')))
        rayon = json.loads(doctor.rayon)
        info = json.loads(doctor.info)
        w_i = json.loads(doctor.work_information)
        p_i = json.loads(doctor.private_information)
        a_i = json.loads(doctor.additional_information)
        b_i = json.loads(doctor.branch_information)

        def get_obj(model, obj_id):
            try:
                return model.objects.using('master').get(id=int(obj_id))
            except:
                return None

        title = get_obj(Title, info.get('title'))
        salutation = get_obj(Salutation, info.get('salutation'))
        grade_user = get_obj(UserGrade, w_i.get('sales_information', {}).get('grade_user'))
        grade_clinic = get_obj(ClinicGrade, w_i.get('sales_information', {}).get('grade_clinic'))
        specialist = get_obj(Specialist, w_i.get('sales_information', {}).get('specialist_id'))

        return {
            'active': "Active" if doctor.is_active else "Not Active",
            'code': doctor.code,
            'apps_bco_id': doctor.jamet_id,
            'rayon_pic_id': rayon.get('id'),
            'rayon_pic_name': rayon.get('rayon'),
            'rayon_coverage_name': rayon.get('rayon_cvr'),
            'dr_full_name': str(info.get('full_name')).strip(),
            'title': f"{title.name}/{title.short_name}" if title else None,
            'salutation': f"{salutation.salutation}/{salutation.short_salutation}" if salutation else None,
            'grade_user': f"{grade_user.name}/{grade_user.alias}" if grade_user else None,
            'grade_clinic': f"{grade_clinic.name}/{grade_clinic.alias}" if grade_clinic else None,
            'spesialis': f"{specialist.short_name}/{specialist.full}" if specialist else None,
            'work_email': w_i.get('job_information', {}).get('work_email'),
            'work_full_address': w_i.get('address', {}).get('fulladdress'),
            'birth_date': p_i.get('citizenship', {}).get('birth_date'),
            'private_email': p_i.get('private_contact', {}).get('email'),
            'interest': [i.get('interest') for i in a_i.get('interest', [])],
            'updated_at': doctor.updated_at.strftime("%d %B %Y %H:%M:%S"),
            'created_at': doctor.created_at.strftime("%d %B %Y %H:%M:%S")
        }
    except DoctorDetail.DoesNotExist:
        return process_doctor_not_found(g)

def process_all_pages(last_page):
    all_data = []
    for i in range(1, last_page + 1):
        logging.info(f"Fetching page {i}")
        data_page = get_data_page(i)
        for g in data_page:
            try:
                data = process_doctor_from_db(g)
                all_data.append(data)
            except Exception as e:
                logging.error(f"[ERROR] Gagal proses dokter ID {g.get('id_dokter')}: {e}")
        time.sleep(1.5)
    return all_data

def save_to_excel(data, folder_path):
    df = pd.DataFrame(data)
    file_path = os.path.join(folder_path, "doctor_database.xlsx")
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return file_path

def create_zip_file(output_dir, files):
    zip_filename = os.path.join(output_dir, 'data_doctor.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file, arcname=os.path.basename(file))
    return zip_filename

class Command(BaseCommand) :
    help = "Save Database to Excel File (.xslx)"

    def handle(self, *args, **kwargs):
        w = datetime.now().time()

        if sfb() == "generate" :
            print(f"Begin process to generate excel at {w.hour} o'clock.")
            logging.info(f"Begin generate excel at {datetime.now()}")
            self.backup_db()
        
        elif sfb() == "backup" :
            print(f"Begin process to backup database at {w.hour} o'clock.")
            logging.info(f"Begin backup databases at {datetime.now()}")
            apps_to_backup = [
                {"app": "master", "database": "master"},
                {"app": "sales", "database": "sales"},
                {"app": "supplier", "database": "supplier"},
                {"app": "human_resource", "database": "human_resource"},
                {"app": "auth", "database": "default"},
            ]

            self.backup_database(apps_to_backup)
        
        elif sfb() == "fullname" :
            print(f"Begin generating full name for the database at {datetime.now().time()}.")
            logging.info(f"Begin generating full name for databases at {datetime.now().time()}.")
            self.full_name()
        
        elif sfb() == "rayon" :
            print(f"Begin generating rayon_name for the database at {datetime.now().time()}.")
            logging.info(f"Begin generating rayon_name for databases at {datetime.now().time()}.")
            self.nam_rayon()

        else :
            print(f"Pass, now is {w.hour} o'clock.")
            pass

    def backup_db(self):
        try:
            folder_path = os.path.join(settings.MEDIA_ROOT, 'output')
            os.makedirs(folder_path, exist_ok=True)
            logging.info("Start backup_db process.")

            last_page = get_last_page(API_URL)
            all_data = process_all_pages(last_page)
            xlsx_file = save_to_excel(all_data, folder_path)

            log_file = os.path.join(folder_path, 'db_to_excel.log')
            zip_file = create_zip_file(folder_path, [xlsx_file, log_file])

            self.stdout.write(self.style.SUCCESS(f"ZIP file created: {zip_file}"))

        except Exception as e:
            logging.error(f"[FATAL] backup_db failed: {e}")
            email = EmailMessage(
                subject=f"Extraction Database Error: {str(e)} at {datetime.now()}",
                body="Backup DB failed, see log file.",
                from_email="satriodasmdi@gmail.com",
                to=["satrio.it@maztafarma.co.id", "taufan.it@maztafarma.co.id"]
            )
            log_file_path = os.path.join(settings.MEDIA_ROOT, 'output', "db_to_excel.log")
            if os.path.exists(log_file_path):
                email.attach_file(log_file_path)
            email.send()
            raise e
    
    def backup_database(self, apps_and_dbs):

        os.makedirs('data_backup', exist_ok=True)
        python_cmd = os.environ.get("PYTHON_CMD", sys.executable)  # default to current Python

        for entry in apps_and_dbs:
            app_label = entry["app"]
            db_alias = entry["database"]
            filename = f"{app_label}.json"
            output_path = os.path.join('data_backup', filename)

            command = [
                python_cmd, "manage.py", "dumpdata", app_label,
                f"--database={db_alias}",
                f"--output={output_path}"
            ]

            try:
                subprocess.run(command, check=True)
                print(f"✔ Backup completed for '{app_label}' to '{output_path}'")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error backing up '{app_label}': {e}")
                email = EmailMessage(
                    subject=f"BACKUP DATABASE ERROR: {str(e)} at {datetime.now()}",
                    body=f"ERROR COOKKKK",
                    from_email="satriodasmdi@gmail.com",
                    to=["satrio.it@maztafarma.co.id", "taufan.it@maztafarma.co.id", "satriodasmdi@gmail.com"]
                )
                email.send()
                logging.error("Error Occured: %s", str(e))
                continue
    
    def full_name(self) :
        print(f"Checking if it can run or not?")
        try :
            print(f"Begin loopnig the databases at {datetime.now().time()}.")
            logging.info(f"Begin loopnig the databases at {datetime.now().time()}.")
            doctors = DoctorDetail.objects.using('sales').filter(
                Q(info__icontains='"full_name": null') |
                Q(info__icontains='"full_name": ""') |
                ~Q(info__icontains='"full_name"')
            )

            print(f"Begin updating the databases at {datetime.now().time()}")
            logging.info(f"Begin updating the databases at {datetime.now().time()}")
            for d in doctors :
                ww = json.loads(d.info)
                dd = DoctorDetail.objects.using('sales').get(id=d.pk)
                dd.info = json.dumps({
                    'first_name' : ww.get('first_name'),
                    'middle_name' : ww.get('middle_name'),
                    'last_name' : ww.get('last_name'),
                    'full_name' : f"{ww.get('first_name')} {ww.get('middle_name')} {ww.get('last_name')}".strip(),
                    'salutation' : ww.get('salutation'),
                    'title' : ww.get('title')
                })
                dd.save()
            print(f"Success updating the databases at {datetime.now().time()}.")
            logging.info(f"Success updating the databases at {datetime.now().time()}.")
        
        except Exception as e :
            email = EmailMessage(
                subject=f"Generate Full_Name ERROR: {str(e)} at {datetime.now()}",
                body=f"ERROR COOKKKK",
                from_email="satriodasmdi@gmail.com",
                to=["satrio.it@maztafarma.co.id", "taufan.it@maztafarma.co.id", "satriodasmdi@gmail.com"]
            )
            email.send()
            logging.error("Error Occured: %s", str(e))
    
    def nam_rayon(self):
        logging.info("Starting rayon update...")

        try:
            conn = requests.get('https://dev-bco.businesscorporateofficer.com/api/master-data-dokter/7')
            last_page = int(conn.json().get('data').get('last_page'))
            logging.info(f"Total page to process: {last_page}")

            for i in range(1, last_page + 1):
                logging.info(f"Fetching page {i}")
                res = requests.get(f'https://dev-bco.businesscorporateofficer.com/api/master-data-dokter/7?page={i}')
                the_data = res.json().get('data').get('data')

                doctors_to_update = []

                for r in the_data:
                    id_dokter = r.get('id_dokter')
                    try:
                        doctor = DoctorDetail.objects.using('sales').get(jamet_id=int(id_dokter))

                        try:
                            rayon_data = json.loads(doctor.rayon or '{}')
                            id_rayon = rayon_data.get('id')
                            rayon = rayon_data.get('rayon')
                        except json.JSONDecodeError:
                            id_rayon = None
                            rayon = None

                        doctor.rayon = json.dumps({
                            'id': id_rayon,
                            'rayon': rayon,
                            'rayon_cvr': r.get('rayon_asal')
                        })

                        doctors_to_update.append(doctor)
                        logging.info(f"Queued update for: {json.loads(doctor.info).get('first_name')}")

                    except DoctorDetail.DoesNotExist:
                        logging.warning(f"Doctor with id_dokter={id_dokter} does not exist.")

                # Save in bulk
                if doctors_to_update:
                    with transaction.atomic(using='sales'):
                        DoctorDetail.objects.using('sales').bulk_update(doctors_to_update, ['rayon'])
                    logging.info(f"Bulk updated {len(doctors_to_update)} doctors from page {i}")

                time.sleep(0.2)

        except Exception as e:
            logging.error(f"Error occurred: {e}")