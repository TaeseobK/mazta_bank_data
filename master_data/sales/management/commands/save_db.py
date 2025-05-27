from django.core.management.base import BaseCommand
import pandas as pd
from sales.models import *
from master.models import *
from django.core.mail import EmailMessage
from datetime import datetime
import json
import zipfile
from django.conf import settings
import os
import logging


folder_path = "master_data/media/output"
log_file = os.path.join(folder_path, "db_to_excel.log")

if not os.path.exists(folder_path) :
    os.makedirs(folder_path)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger().addHandler(logging.StreamHandler())

class Command(BaseCommand) :
    help = "Save Database to Excel File (.xslx)"

    def handle(self, *args, **kwargs):
        now = datetime.now()
        print(f"Saving Database to Excel Start at {datetime.now()}")
        logging.info("Start exporting database at %s", now)

        try :
            doctors = DoctorDetail.objects.using('sales').filter(is_active=True).all()
            logging.info("Fetched %d active doctors", doctors.count())

            info = []
            for d in doctors :
                d.info = json.loads(d.info)
                salutation = Salutation.objects.using('master').get(id=int(d.info.get('salutation')))
                title = Title.objects.using('master').get(id=int(d.info.get('title')))
                infos = {
                    "doctor_id" : d.pk,
                    "first_name" : d.info.get('first_name'),
                    "middle_name" : d.info.get('middle_name'),
                    "last_name" : d.info.get('last_name'),
                    "full_name" : d.info.get('full_name'),
                    "salutation" : f"{salutation.short_salutation} - {salutation.salutation}",
                    "title" : f"{title.short_name} - {title.name}"
                }
                info.append(infos)
            logging.info("Proceed 'Info' data for doctors")
            print("Proceed 'Info' data for doctors")

            rayon = []
            for r in doctors :
                r.rayon = json.loads(r.rayon)
                rayons = {
                    "doctor_id" : r.pk,
                    "rayon_id" : r.rayon.get('id'),
                    "rayon_name" : r.rayon.get('rayon')
                }
                rayon.append(rayons)
            logging.info("Proceed 'Rayon' data for doctors")
            print("Proceed 'Rayon' data for doctors")

            woi = []
            for wi in doctors :
                wi.work_information = json.loads(wi.work_information)
                grade_clinic = ClinicGrade.objects.using('master').get(id=int(wi.work_information.get('sales_information').get('grade_clinic')))
                grade_clinic.range_clinic = json.loads(grade_clinic.range_clinic)
                grade_user = UserGrade.objects.using('master').get(id=int(wi.work_information.get('sales_information').get('grade_user')))
                grade_user.range_user = json.loads(grade_user.range_user)
                specialist = Specialist.objects.using('master').get(id=int(wi.work_information.get('sales_information').get('specialist_id')))

                max_measure = grade_user.range_user.get('max').get('measure')
                if max_measure == "Thousand" :
                    max_digits = int(1000)
                elif max_measure == "Million" :
                    max_digits = int(1000000)
                elif max_measure == "Billion" :
                    max_digits = int(1000000000)

                min_measure = grade_user.range_user.get('min').get('measure')
                if min_measure == "Thousand" :
                    min_digits = int(1000)
                elif min_measure == "Million" :
                    min_digits = int(1000000)
                elif min_digits == "Billion" :
                    min_digits = int(1000000000)

                work_informations = {
                    "doctor_id" : wi.pk,
                    "work_address_street_1" : wi.work_information.get('address').get('street_1'),
                    "work_address_street_2" : wi.work_information.get('address').get('street_2'),
                    "work_address_city" : wi.work_information.get('address').get('city'),
                    "work_address_country" : wi.work_information.get('address').get('country'),
                    "work_address_zip" : wi.work_information.get('address').get('zip'),
                    "work_address_fulladdress" : wi.work_information.get('address').get('fulladdress'),

                    #Job Information
                    "work_job_information_workspace_name" : wi.work_information.get('job_information').get('workspace_name'),
                    "work_job_information_job_position" : wi.work_information.get('job_information').get('job_position'),
                    "work_job_information_work_phone" : wi.work_information.get('job_information').get('work_phone'),
                    "work_job_information_work_mobile" : wi.work_information.get('job_information').get('work_mobile'),
                    "work_job_information_work_email" : wi.work_information.get('job_information').get('work_email'),

                    #sales_information
                    "work_sales_information_grade_user" : f"{grade_user.name}, (Max {int(grade_user.range_user.get('max').get('value')) * max_digits}, Min {int(grade_user.range_user.get('min').get('value')) * min_digits})",
                    "work_sales_information_grade_clinic" : f"{grade_clinic.name}, (Max {grade_clinic.range_clinic.get('max_value')} Clinic, Min {grade_clinic.range_clinic.get('min_value')} Clinic)",
                    "priority" : "Priority" if int(wi.work_information.get('sales_information').get('priority')) == 1 else "Not Priority",
                    "specialist" : f"{specialist.short_name} - {specialist.full}",

                    #system_information
                    "work_system_information_accurate_code" : wi.work_information.get('system_information').get('accurate_code')
                }
                woi.append(work_informations)
            logging.info("Proceed 'Work Information' data for doctors")
            print("Proceed 'Work Information' data for doctors")

            pii = []
            for pi in doctors :
                pi.private_information = json.loads(pi.private_information)
                private_informations = {
                    "doctor_id" : pi.pk,
                    "private_address_street_1" : pi.private_information.get('private_contact').get('address').get('street_1'),
                    "private_address_street_2" : pi.private_information.get('private_contact').get('address').get('street_2'),
                    "private_address_city" : pi.private_information.get('private_contact').get('address').get('city'),
                    "private_address_state" : pi.private_information.get('private_contact').get('address').get('state'),
                    "private_address_country" : pi.private_information.get('private_contact').get('address').get('country'),
                    "private_address_zip" : pi.private_information.get('private_contact').get('address').get('zip'),

                    "private_email" : pi.private_information.get('private_contact').get('email'),
                    "private_phone" : pi.private_information.get('private_contact').get('phone'),

                    #Citizenship
                    "private_citizenship_nationality" : pi.private_information.get('citizenship').get('nationality'),
                    "private_citizenship_gender" : pi.private_information.get('citizenship').get('gender'),
                    "private_citizenship_birth_date" : pi.private_information.get('citizenship').get('birth_date'),
                    "private_citizenship_birth_place" : pi.private_information.get('citizenship').get('birth_place'),
                    "private_citizenship_religion" : pi.private_information.get('citizenship').get('religion'),

                    #Education
                    "private_education_certification" : pi.private_information.get('education').get('certification'),
                    "private_education_field_study" : pi.private_information.get('education').get('field_study'),
                    "private_education_school_name" : pi.private_information.get('education').get('school_name'),
                    "marital_status" : pi.private_information.get('family').get('marital_status')
                }
            logging.info("Proceed 'Private Information' data for doctors")
            print("Proceed 'Private Information' data for doctors")            

            spouse = []
            for sp in doctors :
                family = sp.private_information.get('family', {})
                spouses = family.get('spouse', [])

                for sps in spouses :
                    spouse.append({
                        "doctor_id": sp.pk,
                        "spouse_firstname": sps.get('firstname', ''),
                        "spouse_middlename": sps.get('middlename', ''),
                        "spouse_lastname": sps.get('lastname', ''),
                        "spouse_fullname": sps.get('fullname', ''),
                        "spouse_birthdate": sps.get('birthdate', ''),
                        "spouse_phone": sps.get('phone', ''),
                        "spouse_mariage_date": sps.get('mariage_date', '')
                    })
            logging.info("Proceed 'Spouse' data for doctors")
            print("Proceed 'Spouse' data for doctors")

            children = []
            for ch in doctors :
                fam = sp.private_information.get('family', {})
                childrens = fam.get('children')

                for chi in childrens :
                    children.append({
                        "doctor_id" : ch.pk,
                        "children_firstname" : chi.get('firstname'),
                        "children_middlename" : chi.get('middlename'),
                        "children_lastname" : chi.get('lastname'),
                        "children_fullname" : chi.get('fullname'),
                        "children_birthdate" : chi.get('birthdate'),
                        "children_phone" : chi.get('phone')
                    })
            logging.info("Proceed 'Children' data for doctors")
            print("Proceed 'Children' data for doctors")

            interest = []
            for inte in doctors :
                addi = json.loads(inte.additional_information).get('interests')
                
                for atr in addi :
                    interest.append({
                        "doctor_id" : inte.pk,
                        "category" : atr.get('category'),
                        "interest" : atr.get('interest')
                    })
            logging.info("Proceed 'Interest' data for doctors")
            print("Proceed 'Interest' data for doctors")

            sosmed = []
            for ss in doctors :
                sss = json.loads(ss.additional_information).get('social_media')

                for tt in sss :
                    sosmed.append({
                        "doctor_id" : ss.pk,
                        "socmed_name" : tt.get('name'),
                        "account_name" : tt.get('account_name')
                    })
            logging.info("Proceed 'Social Media' data for doctors")
            print("Proceed 'Social Media' data for doctors")

            best_time = []
            for bst in doctors :
                bstt = json.loads(bst.additional_information).get('base_time')
                best_time.append({
                    "doctor_id" : bst.pk,
                    "best" : bstt.get('base'),
                    "time" : bstt.get('time')
                })
            logging.info("Proceed 'Best Time' data for doctors")
            print("Proceed 'Best Time' data for doctors")

            branch = []
            for brnch in doctors :
                for brch in json.loads(brnch.branch_information) :
                    branch.append({
                        "doctor_id" : brnch.pk,
                        "branch_name" : brch.get('branch_name'),
                        "branch_est_data" : brch.get('branch_established_date'),
                        "branch_address_street_1" : brch.get('branch_street_1'),
                        "branch_address_street_2" : brch.get('branch_street_2'),
                        "branch_address_city" : brch.get('branch_city'),
                        "branch_address_state" : brch.get('branch_state'),
                        "branch_address_country" : brch.get('branch_country'),
                        "branch_address_zip" : brch.get('branch_zip')
                    })
            logging.info("Proceed 'Branch' data for doctors")
            print("Proceed 'Branch' data for doctors")

            info_data = pd.DataFrame(info)
            rayon_data = pd.DataFrame(rayon)
            woi_data = pd.DataFrame(woi)
            pii_data = pd.DataFrame(pii)
            sps_data = pd.DataFrame(spouse)
            chi_data = pd.DataFrame(children)
            inte_data = pd.DataFrame(interest)
            sos_data = pd.DataFrame(sosmed)
            bst_data = pd.DataFrame(best_time)
            brc_data = pd.DataFrame(branch)
            logging.info("Proceed to zipping all data for doctors")
            print("Proceed to zipping all data for doctors")
            
            logging.info("Saving database to a excel file")
            print("Saving database to a excel file")
            with pd.ExcelWriter(os.path.join(folder_path, "doctor_database.xlsx"), engine="openpyxl") as writer :
                info_data.to_excel(writer, sheet_name="Info", index=False)
                rayon_data.to_excel(writer, sheet_name="Rayon", index=False)
                woi_data.to_excel(writer, sheet_name="Work_Information", index=False)
                pii_data.to_excel(writer, sheet_name="Private_Information", index=False)
                sps_data.to_excel(writer, sheet_name="Spouses", index=False)
                chi_data.to_excel(writer, sheet_name="Childrens", index=False)
                inte_data.to_excel(writer, sheet_name="Interest", index=False)
                sos_data.to_excel(writer, sheet_name="Social_Media", index=False)
                bst_data.to_excel(writer, sheet_name="Best_Time", index=False)
                brc_data.to_excel(writer, sheet_name="Branches", index=False)
            logging.info("Saving database successfully")
            print("Saving database successfully")
            
            logging.info("Merging to zip fle")
            output_dir = os.path.join(settings.MEDIA_ROOT, 'output')
            zip_filename = os.path.join(output_dir, 'data_doctor.zip')

            files_to_zip = [
                os.path.join(output_dir, 'doctor_database.xlsx'),
                os.path.join(output_dir, 'db_to_excel.log')
            ]

            try :
                with zipfile.ZipFile(zip_filename, 'w') as zipf :
                    for file in files_to_zip :
                        if os.path.exists(file) :
                            arcname = os.path.basename(file)
                            zipf.write(file, arcname=arcname)
                
                self.stdout.write(self.style.SUCCESS(f"ZIP file created success filename : {zip_filename}"))
                
            
            except Exception as e :
                self.stderr.write(self.style.ERROR(f"Failed to create ZIP file: {str(e)}"))

        except Exception as e :
            email = EmailMessage(
                subject=f"Extraction Database Error: {str(e)} at {datetime.now()}",
                body=f"EEEEEEEEEEEEEEERRRRRRRRRRRRRRRROOOOOOOOOOOOOORRRRRRRRRRRRRRR",
                from_email="satriodasmdi@gmail.com",
                to=["satrio.it@maztafarma.co.id", "taufan.it@maztafarma.co.id", "satriodasmdi@gmail.com"]
            )
            email.attach_file(os.path.join(folder_path ,"db_to_excel.log"))
            email.send()
            logging.error("Error Occured: %s", str(e))
            raise e