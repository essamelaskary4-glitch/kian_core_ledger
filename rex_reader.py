import sqlite3
import os
from datetime import datetime

# =================================================================
# REX-LEDGER READER: وحدة قراءة سجل الحقيقة الأبدي
# =================================================================

DB_NAME = "ees_core_ledger.db"

def read_ledger_records():
    """
    يتصل بقاعدة البيانات ويقرأ جميع السجلات في REX_Ledger.
    """
    if not os.path.exists(DB_NAME):
        print(f"❌ خطأ: لم يتم العثور على قاعدة البيانات {DB_NAME}. تأكد من تشغيل ees_core_v1_0.py أولاً.")
        return []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # الأعمدة: (id, timestamp, data_payload, current_hash, previous_hash)
    cursor.execute("SELECT id, timestamp, data_payload, current_hash, previous_hash FROM REX_Ledger ORDER BY id ASC")
    records = cursor.fetchall()
    conn.close()
    return records

def display_records(records):
    """
    يعرض السجلات بتنسيق مُنظَّم.
    """
    print("\n=====================================================================================================")
    print("📜 سجل الوجود الأبدي (REX-Ledger) - توثيق قرارات الكيان 📜")
    print("=====================================================================================================")
    
    if not records:
        print("السجل فارغ.")
        return

    # تنسيق الطباعة
    print(f"{'ID':<4} | {'Timestamp (UTC)':<25} | {'Data Payload':<60} | {'Current Hash (Partial)':<15}")
    print("-" * 140)

    for record in records:
        record_id = record[0]
        timestamp = record[1]
        data_payload = record[2]
        current_hash = record[3]
        
        # تحويل الطابع الزمني إلى تنسيق قابل للقراءة
        dt_object = datetime.fromtimestamp(timestamp)
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')

        # اقتصار الهاش للعرض
        hash_preview = current_hash[:12] + "..."
        
        # تلوين خاص لسجل الموافقة (APPROVED) لتسهيل الرصد
        if "APPROVED" in data_payload:
            color_code = '\033[92m'  # الأخضر
            reset_code = '\033[0m'
        else:
            color_code = ''
            reset_code = ''

        print(f"{record_id:<4} | {formatted_time:<25} | {color_code}{data_payload:<60}{reset_code} | {hash_preview:<15}")
    
    print("=====================================================================================================")
    print(f"إجمالي السجلات المُوثقة: {len(records)}")
    print("=====================================================================================================")


if __name__ == '__main__':
    all_records = read_ledger_records()
    display_records(all_records)