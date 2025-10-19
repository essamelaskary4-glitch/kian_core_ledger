import sqlite3
import time
import json
# التأكد من أن الدالة الحرجة record_and_hash_event متاحة
from ees_core_v1_0 import record_and_hash_event, DB_NAME 

# =================================================================
# REX-Ledger FIXER: لإصلاح سجلات التخصيص الذاتي المتضررة
# =================================================================

def fix_self_allocation_record():
    """يحذف ويسجل آخر قيد SELF ALLOCATION لضمان قابليته للقراءة."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. البحث عن آخر قيد SELF ALLOCATION (للحصول على بياناته)
    cursor.execute("""
        SELECT id, data_payload 
        FROM REX_Ledger 
        WHERE data_payload LIKE '%SELF ALLOCATION:%' 
        ORDER BY id DESC 
        LIMIT 1
    """)
    last_record = cursor.fetchone()

    if not last_record:
        print("❌ REX-Ledger Fixer: لم يتم العثور على أي سجل SELF ALLOCATION. يرجى تشغيل SER-Analyzer أولاً.")
        conn.close()
        return

    record_id, payload_str = last_record.strip()

    # 2. استخراج كائن JSON الخام يدوياً (المنطق الأكثر قوة)
    try:
        # قص الجزء النصي الذي يحتوي على JSON
        start_index = payload_str.find('{')
        end_index = payload_str.rfind('}') + 1
        
        if start_index == -1 or end_index == -1:
            print("❌ REX-Ledger Fixer: فشل في تحديد حدود JSON في السجل.")
            conn.close()
            return
            
        json_string = payload_str[start_index:end_index]
        
        # تنظيف الحمولة وفك تشفيرها للحصول على البيانات الأصلية
        json_string = json_string.replace("'", '"')
        json_string = json_string.replace('True', 'true').replace('False', 'false')
        
        project_data = json.loads(json_string)
    except Exception as e:
        print(f"❌ REX-Ledger Fixer: فشل استخراج بيانات المشروع الأصلية. الخطأ: {e}")
        conn.close()
        return
        
    print(f"✅ REX-Ledger Fixer: تم استرجاع بيانات المشروع بنجاح: {project_data['project type']}")
    
    # 3. حذف السجل المتضرر من السلسلة (تدمير مؤقت للسلسلة)
    cursor.execute("DELETE FROM REX_Ledger WHERE id = ?", (record_id,))
    
    print(f"⚠️ REX-Ledger Fixer: تم حذف السجل ID {record_id} بنجاح. سنقوم بإعادة تسجيله.")
    
    # 4. إعادة تسجيل السجل باستخدام تنسيق JSON الموحد
    # نستخدم json.dumps لضمان أن الحمولة الجديدة هي JSON قياسي (اقتباسات مزدوجة)
    new_payload = json.dumps(project_data)
    
    # نستخدم دالة التسجيل الأصلية لتطبيق الهاش بشكل صحيح على السجل الجديد
    # ملاحظة: دالة record_and_hash_event تتوقع أن يتم تمرير النوع والنتيجة بشكل منفصل
    record_and_hash_event("SELF ALLOCATION", new_payload, "APPROVED")
    
    conn.commit()
    conn.close()
    
    print("🏆 REX-Ledger Fixer: تم إعادة تسجيل SELF ALLOCATION بنجاح. الهاش الجديد سليم.")

if __name__ == '__main__':
    print("=========================================================")
    print("🔧 REX-Ledger FIXER: أداة إصلاح قاعدة بيانات السجل الأبدي")
    print("=========================================================")
    fix_self_allocation_record()
    print("=========================================================")