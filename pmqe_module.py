import sqlite3
import json
import time
from ees_core_v1_0 import DB_NAME, get_ledger_contents, record_and_hash_event

# =================================================================
# PMQE MODULE: PREVENTIVE MAINTENANCE AND QUALITY ENHANCEMENT V1.0
# =================================================================

def assess_performance():
    """تقييم الأداء بناءً على آخر سجل RCM لتحديد الحاجة لدورة تخصيص ذاتي جديدة."""
    print("\n--- PMQE Module: بدء تقييم الأداء الوقائي ---")
    
    # 1. البحث عن آخر نتيجة RCM في السجل
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data_payload FROM REX_Ledger 
        WHERE data_payload LIKE '%RCM_CYCLE_END%' 
        ORDER BY id DESC LIMIT 1
    """)
    last_rcm_record = cursor.fetchone()
    conn.close()
    
    if last_rcm_record:
        payload_text = last_rcm_record[0]
        
        # 2. تحليل نتيجة RCM
        if "RCM_SUCCESS" in payload_text:
            print("✅ تم رصد: RCM_SUCCESS. الأداء الحالي مستقر/مثالي.")
            # 3. اتخاذ القرار: إطلاق دورة تخصيص ذاتي جديدة
            
            # تسجيل الحدث الذي يطلق دورة التخصيص الذاتي الجديدة
            pmqe_action = "TRIGGER_SELF_ALLOCATION"
            record_and_hash_event("PMQE_ASSESSMENT", f"Status: RCM_SUCCESS. Action: {pmqe_action}", "SUCCESS")
            
            print(f"🎉 تم إطلاق الأمر: {pmqe_action}. يجب تشغيل ser_analyzer.py لتحديد الهدف التنموي التالي.")
            return True
        else:
            print("⚠️ تم رصد: فشل RCM أو حالة غير مستقرة. لا يتم إطلاق دورة تخصيص ذاتي جديدة.")
            return False
    else:
        print("❌ لم يتم العثور على سجل RCM سابق. لا يمكن إجراء تقييم للأداء.")
        return False

if __name__ == '__main__':
    assess_performance()