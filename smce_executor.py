import ees_core_v1_0 as ees
import json
import time

# =================================================================
# SMCE-Executor Module V1.1 (Fixed Logic)
# وحدة التنفيذ المنهجي - تفعيل الانتقال إلى RCM
# =================================================================

def fetch_last_self_allocation_approved():
    """
    استرجاع آخر أمر SELF_ALLOCATION تم الموافقة عليه (SER_APPROVED).
    يتم تجاهل أوامر CORE_REVERT والاوامر المرفوضة.
    :return: قاموس يحتوي على الحمولة (Payload) أو None.
    """
    # استرجاع آخر 10 سجلات لتقليل زمن البحث (يمكن زيادته إذا لزم الأمر)
    # ملاحظة: دالة get_ledger_contents تم تعديلها في ees_core_v1_0.py لدعم limit=None
    records = ees.get_ledger_contents(limit=10)
    
    # البحث عن آخر سجل SELF_ALLOCATION تم الموافقة عليه
    for record in records:
        if record['event_type'] == 'SELF_ALLOCATION':
            # التحقق من أن النتيجة هي SER_APPROVED
            if 'Result: SER_APPROVED' in record['data_payload']:
                # استخلاص الحمولة (Payload) من حقل data_payload
                # يتم فصل الحمولة عن حقل النتيجة (Result) المضاف في ees_core
                try:
                    # الحمولة تكون في الجزء الأول قبل ", Result: "
                    payload_str = record['data_payload'].split(', Result: ')[0]
                    # تحويل الحمولة JSON إلى قاموس Python
                    return json.loads(payload_str)
                except (json.JSONDecodeError, IndexError) as e:
                    # إذا فشل التحليل، ننتقل للسجل السابق
                    print(f"❌ خطأ في تحليل الحمولة (ID: {record.get('id')}): {e}. يتم تجاهل هذا السجل.")
                    continue
                    
    return None

def execute_self_allocation():
    """تنفيذ المهمة الموافق عليها وإطلاق دورة RCM."""
    print("--- SSE-Core: SMCE Executor - بدأ التنفيذ المنهجي وحدة ---")
    
    # استخدام الدالة المُعدَّلة لجلب الأمر المعتمد فقط
    approved_project = fetch_last_self_allocation_approved()

    if approved_project:
        project_type = approved_project.get("project_type", "UNKNOWN")
        cost = approved_project.get("cost", 0.00)
        
        print(f"✅ التنفيذ بدأ: تم العثور على أمر SELF ALLOCATION مُعتمد")
        print(f"✅ المشروع نوع : {project_type}")
        print(f"✅ الفقرة التكلفة : {cost:.2f}$")

        # تسجيل بدء التنفيذ في السجل الأبدي
        ees.record_and_hash_event("EXECUTION_START", f"Project: {project_type}", "SUCCESS")
        
        # الانتقال إلى وحدة RCM
        print("--- الأبدي الخلق (وحدة RCM) إلى الانتقال : نجاح ---")
        ees.record_and_hash_event("RCM_TRANSITION", f"Project: {project_type}", "SUCCESS")
        
        # ملاحظة: في المشروع الكامل، سيتم هنا استدعاء rcm_module.py فعلياً
        
    else:
        print("❌ التنفيذ لم يبدأ: لم يتم العثور على أمر SELF ALLOCATION مُعتمد للتنفيذ.")
        print("💡 التغذية الراجعة: يجب تشغيل ser_analyzer.py للحصول على قرار معتمد.")
    
    print("--- انتهت وحدة التنفيذ المنهجي ---")


if __name__ == '__main__':
    execute_self_allocation()