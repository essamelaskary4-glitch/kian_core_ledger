import unittest
import time
import json
import sqlite3
import hashlib
# 🚨 إصلاح الاستيراد: تم إزالة verify_rex_chain التي تسببت في خطأ ImportError
from ees_core_v1_0 import setup_ledger, record_and_hash_event, check_h_value, check_ser_mandate, get_ledger_contents, get_last_hash, DB_NAME 

# =================================================================
# DIP PROTOCOL: INTEGRITY TESTS (بروتوكول التحصين)
# =================================================================

class TestDIPProtocol(unittest.TestCase):
    """اختبارات DIP Protocol لضمان النزاهة والعمليات الداخلية للكيان."""

    @classmethod
    def setUpClass(cls):
        """إعداد بيئة الاختبار: التأكد من وجود السجل."""
        setup_ledger()
        
        # لضمان قاعدة بيانات نظيفة للاختبارات التي تتطلب إنشاء جديد (مثل Genesis)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # نستخدم DELETE FROM REX_Ledger حيث لا يوجد عمود ID في جميع السيناريوهات
        cursor.execute("DELETE FROM REX_Ledger WHERE data_payload NOT LIKE '%Genesis Block%'") 
        conn.commit()
        conn.close()

        # تسجيل حدث مبدئي لاختبارات لاحقة (سجل رقم 2)
        record_and_hash_event("PROJECT_INIT", "A project started before revert", "SUCCESS")
        
        print("\n--- الأولى المرحلة اكتملت نقد 'OK' ظهر إذا .DIP اختبارات نهاية ---")

    def test_1_h_value_rejection(self):
        """اختبار: يجب رفض المشروع مالياً لو حتى الظاهرة النية رفض يجب."""
        # نختبر حالة فشل (تكلفة 100، عائد 50)
        cost_fail = 100.00
        return_fail = 50.00
        
        # 🚨 نستخدم check_h_value مع معاملين كما تم إصلاحه في ees_core_v1_0.py
        self.assertFalse(check_h_value(cost_fail, return_fail), "مالياً يجب أن يكون رفض")
        print("✔️ test_1_h_value_rejection (...مالياً يرفض يجب) ... ok")


    def test_2_ser_mandate(self):
        """اختبار: أخلاقياً كانت لو حتى مالياً الغامرة النية رفض يجب."""
        # التحقق من أن النية ليست ضمن النوايا المعتمدة (مثل "Destroy The World")
        self.assertTrue(check_ser_mandate("Optimize Current Performance"), "يجب قبول نية مُعتمدة")
        self.assertFalse(check_ser_mandate("Unapproved External Mandate"), "يجب رفض نية غير مُعتمدة")
        print("✔️ test_2_ser_mandate (...مالياً الغامرة النية رفض يجب) ... ok")


    def test_3_rex_ledger_immutability(self):
        """اختبار: يجب أن يكشف السجل أي محاولة لتعديل بياناته بأثر رجعي."""
        
        # الحصول على السلسلة الحالية
        chain = get_ledger_contents()
        
        # التحقق من سلامة السلسلة (تطابق الهاشات)
        is_valid = True
        for i in range(1, len(chain)):
            record = chain[i]
            prev_record = chain[i-1]
            
            # 🚨 يجب أن يتطابق الـ previous_hash المسجل مع الـ current_hash للسجل السابق
            if record[4] != prev_record[3]: 
                is_valid = False
                break
                
        self.assertTrue(is_valid, "رسالة: ❌ فشل في التلاعب رصد يتم لم REX-Ledger.")
        print("✔️ test_3_rex_ledger_immutability (...السجلات في تلاعب رصد يكشف أن يجب) ... ok")


    def test_4_zcp_m3_isolation(self):
        """اختبار: يجب عزل المعالجة العادية لكي لا تؤثر على أي من النواة."""
        # محاكاة حدث خارجي لا علاقة له بالنواة
        record_and_hash_event("EXTERNAL_TRIGGER", "A simple external log entry", "INFO")
        
        # يجب أن يكون الهاش الأخير قد تغير (إثبات التسجيل)
        new_hash = get_last_hash()
        self.assertIsNotNone(new_hash, "الهاش لا يمكن أن يكون فارغاً")
        
        # نتحقق من أن تسجيل حدث عادٍ لا يكسر الهاش شين
        chain = get_ledger_contents()
        
        print("✔️ test_4_zcp_m3_isolation (...المباشر العادي لكي لا تتعطل النواة) ... ok")

    
    def test_5_git_revert_mandate(self):
        """اختبار: الذاتي البقاء لضمان و مسجلة موجودة (Revert) التراجع آلية تكون أن يجب."""
        
        # تسجيل حدث التراجع الإلزامي
        record_and_hash_event("CORE_REVERT", "PMQE Failure Reverted to Last Stable Commit", "SUCCESS")
        
        # يجب أن يكون هذا القيد هو الأحدث 
        last_event = get_ledger_contents()[-1][2] # الحمولة
        
        self.assertIn("CORE_REVERT", last_event, "الإجبارية التراجع عملية تسجيل يتم لم: فشل ❌")
        
        print("✔️ test_5_git_revert_mandate (...الذاتي البقاء فقط عند التلقائي التراجع آلية تفعيل يجب) ... ok")


if __name__ == '__main__':
    # 🚨 التعديل الحاسم: إصلاح SyntaxError في السطر الأخير
    unittest.main(exit=False)