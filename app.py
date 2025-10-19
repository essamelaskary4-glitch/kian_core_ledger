# File: app.py - الكود الكامل المُعدَّل
# الهدف: تفعيل مسار /api/v1/event/record

from flask import Flask, request, jsonify
import json
import sqlite3
import os
import sys

# *****************************************************************
# 1. تحديث مسار الاستيراد
# *****************************************************************
# الإجراء الإلزامي لـ PythonAnywhere لضمان عمل الاستيراد
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# استيراد الدوال الأساسية من النواة
from ees_core_v1_0 import setup_ledger, record_and_hash_event, get_ledger_contents

# *****************************************************************
# 2. إعداد التطبيق (App Setup)
# *****************************************************************
app = Flask(__name__)
# التأكد من إنشاء قاعدة البيانات إذا لم تكن موجودة عند تشغيل التطبيق
setup_ledger()

# *****************************************************************
# 3. المسار الحالي (summarize) - تم للتحقق من النشر
# *****************************************************************
@app.route('/')
def home():
    """مسار اختبار بسيط للتحقق من تشغيل الخادم."""
    return "Kian_AAL Web Core is Operational."

@app.route('/summarize')
def summarize():
    """مسار قديم تم استخدامه للتأكد من وصول الطلبات."""
    return jsonify({
        "status": "Operational",
        "service": "summarize",
        "message": "Service is running."
    })

# *****************************************************************
# 4. المسار الجديد: تسجيل الأحداث السيادية (المحور 2)
# *****************************************************************
@app.route('/api/v1/event/record', methods=['POST'])
def record_sovereign_event():
    """
    تسجيل حدث سيادي جديد في REX-Ledger.
    يتوقع حمولة JSON تحتوي على 'event_type' و 'data_payload'.
    """
    if request.is_json:
        content = request.get_json()
        
        event_type = content.get('event_type')
        data_payload = content.get('data_payload')
        
        # التحقق من المدخلات الإلزامية
        if not event_type or not data_payload:
            return jsonify({"status": "FAILURE", 
                            "message": "Missing 'event_type' or 'data_payload' in request."}), 400

        try:
            # استدعاء دالة التسجيل المُحصّنة من ees_core_v1_0.py
            new_hash = record_and_hash_event(event_type, json.dumps(data_payload), "SUCCESS")
            
            return jsonify({
                "status": "RECORD_SUCCESS",
                "message": "Sovereign event recorded successfully.",
                "event_type": event_type,
                "new_block_hash": new_hash
            }), 201

        except Exception as e:
            # تسجيل أي فشل داخلي كحدث CORE_FAILURE
            record_and_hash_event("CORE_FAILURE", json.dumps({"reason": str(e), "data": data_payload}), "FAILURE")
            return jsonify({
                "status": "CRITICAL_FAILURE",
                "message": f"An internal error occurred during recording. Consult CORE_FAILURE logs. Error: {str(e)}"
            }), 500
            
    return jsonify({"status": "FAILURE", "message": "Request must be JSON."}), 415

# *****************************************************************
# 5. تشغيل التطبيق محلياً (لا يتم استخدامه في PythonAnywhere)
# *****************************************************************
if __name__ == '__main__':
    app.run(debug=True)
