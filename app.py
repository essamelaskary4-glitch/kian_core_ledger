# Kian_AAL Web Core - Final Version (Axis 2 Ready)
# FIX: Renamed Flask instance to 'application' for PythonAnywhere WSGI compatibility.

from flask import Flask, request, jsonify
import json
import sqlite3
import os
import sys

# 1. إعداد المسار (Path Setup)
# هذا يضمن أن الكود يمكنه استيراد الوحدات الموجودة في المجلد الرئيسي (kian_core_ledger).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# استيراد وحدة REX-Ledger CORE
from ees_core_v1_0 import setup_ledger, record_and_hash_event, get_ledger_contents


# *****************************************************************
# 2. إعداد التطبيق (App Setup) - التعديل الأول
# قمنا بتغيير اسم المتغير من 'app' إلى 'application'
# *****************************************************************
application = Flask(__name__) 
setup_ledger()

# *****************************************************************
# 3. المسارات العامة
# يجب الآن استخدام 'application.route' بدلاً من 'app.route'
# *****************************************************************

@application.route('/')
def home():
    """مسار اختبار بسيط للتحقق من تشغيل الخادم."""
    return "Kian_AAL Web Core is Operational."

@application.route('/summarize')
def summarize():
    """مسار اختبار للتأكد من أن قاعدة البيانات تعمل بشكل صحيح."""
    try:
        # استرجاع محتويات السجل
        ledger_data = get_ledger_contents()
        return jsonify({
            "status": "Operational",
            "service": "Summarize (Axis 1)",
            "message": f"Successfully retrieved {len(ledger_data)} records.",
            "data": ledger_data
        })
    except Exception as e:
        return jsonify({
            "status": "Error",
            "service": "summarize",
            "message": f"An error occurred while accessing the ledger: {str(e)}"
        }), 500

# *****************************************************************
# 4. مسار المحور 2: تسجيل الأحداث السيادية (POST /api/v1/event/record)
# *****************************************************************

@application.route('/api/v1/event/record', methods=['POST'])
def record_sovereign_event():
    """
    يتلقى حمولة JSON لتسجيل حدث سيادي في سجل REX-Ledger.
    المدخلات: {"event_type": "STRING", "data_payload": {}}
    المخرجات: JSON يؤكد التسجيل ورقم السجل.
    """
    if request.is_json:
        data = request.get_json()
        
        event_type = data.get('event_type')
        data_payload = data.get('data_payload')

        # التحقق من البيانات المطلوبة
        if not event_type or not isinstance(data_payload, dict):
            return jsonify({
                "status": "INPUT_ERROR",
                "message": "Missing 'event_type' or 'data_payload' (must be an object)."
            }), 400

        try:
            # تسجيل الحدث في السجل (Ledger)
            record_id, hash_value = record_and_hash_event(event_type, data_payload)

            return jsonify({
                "status": "RECORD_SUCCESS",
                "message": "Sovereign event recorded successfully.",
                "record_id": record_id,
                "record_hash": hash_value,
                "event_type": event_type
            }), 201

        except Exception as e:
            # في حالة فشل الاتصال بقاعدة البيانات أو خطأ آخر
            return jsonify({
                "status": "DATABASE_ERROR",
                "message": f"Failed to record event due to server error: {str(e)}"
            }), 500
    else:
        return jsonify({
            "status": "INPUT_ERROR",
            "message": "Content-Type must be application/json."
        }), 415

# *****************************************************************
# 5. تشغيل التطبيق محلياً (تعديل طفيف)
# *****************************************************************
if __name__ == '__main__':
    # التعديل الثالث: يجب استخدام 'application' هنا أيضاً لتشغيل التطبيق محلياً
    application.run(debug=True)
