import os

import pandas as pd
import numpy as np

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    flash
)

from models import Appointment
from routes.auth_helpers import admin_required


analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/analytics"
)


UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "uploads/reports"


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


def get_database_dataframe():

    appointments = Appointment.query.all()

    records = []

    for appointment in appointments:

        records.append({
            "appointment_id": appointment.id,
            "patient_id": appointment.patient_id,
            "patient_name": appointment.patient.name,
            "doctor_id": appointment.doctor_id,
            "doctor_name": appointment.doctor.name,
            "date": appointment.date,
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        })

    columns = [
        "appointment_id",
        "patient_id",
        "patient_name",
        "doctor_id",
        "doctor_name",
        "date",
        "diagnosis",
        "status"
    ]

    df = pd.DataFrame(records, columns=columns)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


def calculate_analytics(df):

    if df.empty:

        return {
            "common_diagnoses": [],
            "doctor_performance": [],
            "status_distribution": [],
            "appointment_trends": [],
            "recovery_time": []
        }


    diagnosis_counts = (
        df["diagnosis"]
        .value_counts()
        .reset_index()
    )

    diagnosis_counts.columns = [
        "diagnosis",
        "count"
    ]

    common_diagnoses = diagnosis_counts.to_dict(
        orient="records"
    )

    doctor_groups = []

    for doctor_name, group in df.groupby("doctor_name"):

        patients_treated = group["patient_id"].nunique()

        total_appointments = len(group)

        recovered_count = (
            group["status"] == "Recovered"
        ).sum()

        recovery_rate = (
            np.mean(
                group["status"] == "Recovered"
            ) * 100
        )

        doctor_groups.append({
            "doctor_name": doctor_name,
            "patients_treated": int(patients_treated),
            "total_appointments": int(total_appointments),
            "recovered": int(recovered_count),
            "recovery_rate": round(
                float(recovery_rate),
                2
            )
        })

    status_counts = (
        df["status"]
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "status",
        "count"
    ]

    status_distribution = status_counts.to_dict(
        orient="records"
    )


    trend_df = (
        df.groupby(
            df["date"].dt.strftime("%Y-%m-%d")
        )
        .size()
        .reset_index(name="count")
    )

    trend_df.columns = [
        "date",
        "count"
    ]

    appointment_trends = trend_df.to_dict(
        orient="records"
    )

    recovery_time = []

    if "recovery_date" in df.columns:

        df["recovery_date"] = pd.to_datetime(
            df["recovery_date"],
            errors="coerce"
        )

        df["recovery_time_days"] = (
            df["recovery_date"] - df["date"]
        ).dt.days

        recovery_df = df.dropna(
            subset=["recovery_time_days"]
        )

        if not recovery_df.empty:

            for diagnosis, group in recovery_df.groupby(
                "diagnosis"
            ):

                values = (
                    group["recovery_time_days"]
                    .dropna()
                    .to_numpy()
                )

                if len(values) > 0:

                    average_days = np.mean(values)

                    recovery_time.append({
                        "diagnosis": diagnosis,
                        "average_recovery_days": round(
                            float(average_days),
                            2
                        )
                    })


    return {
        "common_diagnoses": common_diagnoses,
        "doctor_performance": doctor_groups,
        "status_distribution": status_distribution,
        "appointment_trends": appointment_trends,
        "recovery_time": recovery_time
    }


@analytics_bp.route(
    "/",
    methods=["GET"],
    strict_slashes=False
)
@admin_required
def analytics_dashboard():

    df = get_database_dataframe()

    analytics = calculate_analytics(df)

    return render_template(
        "analytics/dashboard.html",
        analytics=analytics
    )


@analytics_bp.route(
    "/upload",
    methods=["POST"]
)
@admin_required
def upload_csv():

    file = request.files.get("file")

    if not file:
        return "Please select a CSV file", 400

    if file.filename == "":
        return "Please select a CSV file", 400

    if not file.filename.lower().endswith(".csv"):
        return "Only CSV files are allowed", 400

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(file_path)

    try:

        df = pd.read_csv(file_path)

    except Exception as error:

        return f"Unable to read CSV file: {error}", 400

    required_columns = [
        "patient_id",
        "patient_name",
        "doctor_id",
        "doctor_name",
        "date",
        "diagnosis",
        "status"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        return (
            "Missing required columns: "
            + ", ".join(missing_columns)
        ), 400

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["date"]
    )

    analytics = calculate_analytics(df)

    return render_template(
        "analytics/dashboard.html",
        analytics=analytics,
        uploaded_file=file.filename
    )


@analytics_bp.route(
    "/export/csv",
    methods=["GET"]
)
@admin_required
def export_csv():

    df = get_database_dataframe()

    analytics = calculate_analytics(df)

    report_rows = []

    for item in analytics["common_diagnoses"]:

        report_rows.append({
            "report_type": "Common Diagnosis",
            "name": item["diagnosis"],
            "value": item["count"]
        })

    for item in analytics["doctor_performance"]:

        report_rows.append({
            "report_type": "Doctor Performance",
            "name": item["doctor_name"],
            "value": item["recovery_rate"]
        })

    for item in analytics["status_distribution"]:

        report_rows.append({
            "report_type": "Status Distribution",
            "name": item["status"],
            "value": item["count"]
        })

    for item in analytics["appointment_trends"]:

        report_rows.append({
            "report_type": "Appointment Trend",
            "name": item["date"],
            "value": item["count"]
        })

    for item in analytics["recovery_time"]:

        report_rows.append({
            "report_type": "Average Recovery Time",
            "name": item["diagnosis"],
            "value": item["average_recovery_days"]
        })

    report_df = pd.DataFrame(report_rows)

    file_path = os.path.join(
        REPORT_FOLDER,
        "analytics_report.csv"
    )

    report_df.to_csv(
        file_path,
        index=False
    )

    return send_file(
        file_path,
        as_attachment=True,
        download_name="analytics_report.csv"
    )


@analytics_bp.route(
    "/export/excel",
    methods=["GET"]
)
@admin_required
def export_excel():

    df = get_database_dataframe()

    analytics = calculate_analytics(df)

    file_path = os.path.join(
        REPORT_FOLDER,
        "analytics_report.xlsx"
    )

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl"
    ) as writer:

        pd.DataFrame(
            analytics["common_diagnoses"]
        ).to_excel(
            writer,
            sheet_name="Diagnoses",
            index=False
        )

        pd.DataFrame(
            analytics["doctor_performance"]
        ).to_excel(
            writer,
            sheet_name="Doctors",
            index=False
        )

        pd.DataFrame(
            analytics["status_distribution"]
        ).to_excel(
            writer,
            sheet_name="Status",
            index=False
        )

        pd.DataFrame(
            analytics["appointment_trends"]
        ).to_excel(
            writer,
            sheet_name="Trends",
            index=False
        )

        pd.DataFrame(
            analytics["recovery_time"]
        ).to_excel(
            writer,
            sheet_name="Recovery",
            index=False
        )

    return send_file(
        file_path,
        as_attachment=True,
        download_name="analytics_report.xlsx"
    )