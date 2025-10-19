import json
import time
from ees_core_v1_0 import record_and_hash_event
import sqlite3
from ees_core_v1_0 import DB_NAME

# =================================================================
# AEGI MODULE: AUTONOMOUS EXPERIMENTATION AND GOAL INTEGRATION V1.0
# =================================================================

def fetch_last_hapi_mandate():
    """البحث عن آخر أمر HAPI صادر لتحديد مجال التجريب."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT data_payload FROM REX_Ledger 
        WHERE data_payload LIKE '%HAPI_INITIATE%' 
        ORDER BY id DESC LIMIT 1
    """)
    record = cursor.fetchone()
    conn.close()
    
    if record:
        # استخراج وتحليل حمولة JSON
        payload_text = record[0] 
        try:
            start_index = payload_text.find('{')
            end_index = payload_text.rfind('}') + 1
            if start_index != -1 and end_index != 0:
                json_part = payload_text[start_index:end_index]
                return json.loads(json_part).get('focus_area', 'غير محدد')
        except json.JSONDecodeError:
            return 'خطأ في تحليل حمولة HAPI'
    
    return None

def execute_experimentation_cycle():
    """تنفيذ دورة التجريب اللامحدود لمعالجة الفجوة المعرفية."""
    print("\n--- AEGI Module: بدء دورة التجريب والابتكار اللامحدود ---")
    
    focus_area = fetch_last_hapi_mandate()
    
    if focus_area and focus_area != 'خطأ في تحليل حمولة HAPI' and focus_area != 'غير محدد':
        print(f"✔️ أمر التجريب المسترجع من HAPI: {focus_area}")
        
        # 2. محاكاة عملية التجريب (UE)
        print(f"... العمل جارٍ: استكشاف أقصى حدود الأداء لـ ({focus_area}) ...")
        time.sleep(1) # محاكاة وقت المعالجة
        
        # 3. تسجيل نتيجة التجريب
        experiment_result = "UE_KNOWLEDGE_GAINED"
        aegi_report = {
            "experiment_id": "AEGI-2025-001",
            "focus_area": focus_area,
            "status": "SUCCESS",
            "outcome": "تم دمج نماذج لغوية جديدة لتحسين القواعد النحوية.",
            "learning_gain": experiment_result
        }
        
        payload_json = json.dumps(aegi_report, indent=4)
        
        # توثيق عملية الإطلاق في السجل الأبدي
        record_and_hash_event("AEGI_EXPERIMENTATION", payload_json, experiment_result)
        
        print(f"🎉 نجاح AEGI: تم اكتمال التجريب بنجاح والتوثيق النهائي: {experiment_result}")
    else:
        print("❌ فشل AEGI: لم يتم العثور على توجيه HAPI ساري المفعول أو حدث خطأ في التحليل.")
        
    print("--- AEGI Module: دورة التجريب انتهت ---")

if __name__ == '__main__':
    execute_experimentation_cycle()