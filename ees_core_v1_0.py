import sqlite3
import time
import hashlib
import json

# =================================================================
# EES-CORE: ETERNAL EXISTENCE REGISTER CORE V1.0 (Fixed & Updated)
# النواة السيادية والسجل الأبدي
# =================================================================

DB_NAME = 'kian_core_ledger.db'

def setup_ledger():
    """تهيئة قاعدة البيانات وإنشاء جدول REX_Ledger إذا لم يكن موجوداً."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # إنشاء الجدول الأساسي
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS REX_Ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                data_payload TEXT NOT NULL,
                current_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL
            )
        """)
        
        # التحقق من وجود سجل التكوين (Genesis Block)
        cursor.execute("SELECT COUNT(*) FROM REX_Ledger WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            # إنشاء سجل التكوين (Genesis Block)
            genesis_payload = json.dumps({"mandate": "Initial Mandate: EES-CORE Genesis V1.0", "integrity": "Chain is intact."})
            genesis_hash = hashlib.sha256(f"{time.time()}{genesis_payload}".encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO REX_Ledger (timestamp, event_type, data_payload, current_hash, previous_hash) 
                VALUES (?, ?, ?, ?, ?)
            """, (time.time(), "GENESIS_BLOCK", genesis_payload, genesis_hash, "0"))
            
            print("✅ تم تأمين السجل الأبدي (Genesis Block) بنجاح.")
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"❌ خطأ قاعدة بيانات في التهيئة: {e}")
        return False

def get_last_hash():
    """استرجاع الهاش الحالي لآخر سجل في REX_Ledger."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # استرجاع الهاش الحالي لآخر سجل (أو 0 إذا كان السجل فارغاً)
    cursor.execute("SELECT current_hash FROM REX_Ledger ORDER BY id DESC LIMIT 1")
    last_hash = cursor.fetchone()
    conn.close()
    
    return last_hash[0] if last_hash else "0"

def calculate_hash(timestamp, event_type, data_payload, previous_hash):
    """حساب الهاش للسجل الجديد."""
    content = f"{timestamp}{event_type}{data_payload}{previous_hash}"
    return hashlib.sha256(content.encode()).hexdigest()

def record_and_hash_event(event_type, data_payload, result):
    """تسجيل حدث جديد مع ربطه بالسجل السابق."""
    
    if not isinstance(data_payload, str):
        data_payload = json.dumps(data_payload)

    previous_hash = get_last_hash()
    current_timestamp = time.time()
    
    # دمج النتيجة في الحمولة قبل حساب الهاش لضمان النزاهة
    full_payload = data_payload + f", Result: {result}"
    
    current_hash = calculate_hash(current_timestamp, event_type, full_payload, previous_hash)
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO REX_Ledger (timestamp, event_type, data_payload, current_hash, previous_hash) 
            VALUES (?, ?, ?, ?, ?)
        """, (current_timestamp, event_type, full_payload, current_hash, previous_hash))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"❌ خطأ قاعدة بيانات أثناء التسجيل: {e}")
        return False

# =================================================================
# التعديل الإلزامي الأول: لقبول معامل 'limit' الاختياري
# =================================================================

def get_ledger_contents(limit=None):
    """
    استرجاع محتويات السجل الأبدي REX_Ledger.
    :param limit: عدد السجلات المراد استرجاعها (اختياري).
    :return: قائمة بالقواميس (records).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = "SELECT id, timestamp, event_type, data_payload, current_hash, previous_hash FROM REX_Ledger ORDER BY id DESC"
    
    # تطبيق شرط الحد إذا تم تمريره
    if limit is not None and isinstance(limit, int) and limit > 0:
        query += f" LIMIT {limit}"

    # هنا كان يحدث خطأ "no such table" قبل الإصلاح الثاني
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # الحصول على أسماء الأعمدة ديناميكياً
    columns = [desc[0] for desc in cursor.description]
    
    # تحويل البيانات إلى قائمة قواميس لسهولة القراءة
    records = []
    for row in rows:
        records.append(dict(zip(columns, row)))
        
    conn.close()
    return records

def check_h_value(project_cost, project_return):
    """
    التحقق من قيمة H (القيمة الأساسية للنزاهة).
    التعليمات: يجب أن تكون القيمة المرجعة أكبر من القيمة المدخلة.
    """
    return project_return > project_cost

def verify_rex_chain():
    """التحقق من سلامة سلسلة الهاش."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # استرجاع جميع السجلات باستثناء سجل التكوين
    cursor.execute("SELECT id, timestamp, event_type, data_payload, current_hash, previous_hash FROM REX_Ledger ORDER BY id ASC")
    blocks = cursor.fetchall()
    conn.close()
    
    # إذا كان هناك أقل من سجلين (Genesis فقط)، فالسلسلة سليمة مبدئياً
    if len(blocks) <= 1:
        return True
        
    for i in range(1, len(blocks)):
        current_block = blocks[i]
        previous_block = blocks[i-1]
        
        # التحقق الأول: هل الـ previous_hash في السجل الحالي يطابق الـ current_hash في السجل السابق؟
        # العنصر رقم 5 هو previous_hash
        # العنصر رقم 4 هو current_hash
        if current_block[5] != previous_block[4]:
            print(f"❌ فشل سلامة السلسلة عند السجل ID: {current_block[0]}. (Previous Hash Mismatch)")
            return False
        
        # التحقق الثاني: إعادة حساب الهاش وتأكيد مطابقة الـ current_hash
        
        # استخراج البيانات المطلوبة:
        timestamp, event_type, data_payload = current_block[1], current_block[2], current_block[3]
        previous_hash_value = previous_block[4] 
        
        # حساب الهاش المتوقع
        expected_hash = calculate_hash(timestamp, event_type, data_payload, previous_hash_value)
        
        # مقارنة الهاش المتوقع بالهاش المسجل في السجل الحالي
        if expected_hash != current_block[4]:
            print(f"❌ فشل سلامة السلسلة عند السجل ID: {current_block[0]}. (Current Hash Mismatch)")
            return False
            
    return True

# =================================================================
# التعديل الإلزامي الثاني: ضمان التهيئة التلقائية (Autonomous Setup)
# هذا يحل مشكلة "no such table: REX_Ledger" عند الاستيراد.
# =================================================================
setup_ledger()

if __name__ == '__main__':
    # لا داعي لاستدعاء setup_ledger() هنا مجددًا
    if verify_rex_chain():
        print("✅ سلامة السلسلة مؤكدة: Chain is intact.")
    else:
        print("❌ تنبيه أمني: فشل التحقق من سلامة السلسلة.")