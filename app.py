from flask import Flask, request, jsonify
import ees_core_v1_0 as ees
import json
import time

# =================================================================
# AAL-CORE Project Generation - Zero_Cost_Monetizable_API
# ملف التطبيق الأساسي (app.py) - Flask
# =================================================================

app = Flask(__name__)
# تهيئة قاعدة البيانات عند بدء التطبيق لضمان وجود جدول REX_Ledger
ees.setup_ledger() 

def simple_summarize(text):
    """وظيفة تلخيص بسيطة (لغرض POC/Zero-Cost)."""
    # لغرض صفر تكلفة، نستخدم أبسط منطق: الاقتصاص إلى 10 كلمات أو 50 حرفًا
    words = text.split()
    if len(words) > 10:
        summary_text = ' '.join(words[:10]) + '...'
    elif len(text) > 50:
        summary_text = text[:50] + '...'
    else:
        summary_text = text
        
    return summary_text, len(words)

def record_api_usage(endpoint, user_input, word_count):
    """توثيق استخدام الـ API في REX-Ledger لضمان النزاهة والتحليل المستقبلي."""
    usage_data = {
        "endpoint": endpoint,
        "input_length": len(user_input),
        "word_count": word_count,
        "monetization_flag": "USAGE_COUNTED"
    }
    # تسجيل حدث "API_USE" في السجل الأبدي
    ees.record_and_hash_event("API_USE", json.dumps(usage_data), "SUCCESS")


@app.route('/api/v1/summarize', methods=['POST'])
def summarize_text_api():
    """الواجهة البرمجية للتلخيص."""
    
    # 1. التحقق من المدخلات
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
        
    data = request.get_json()
    input_text = data.get('text', '')
    
    if not input_text or len(input_text) > 500:
        return jsonify({"error": "Invalid or missing 'text' field. Max 500 chars."}), 400
        
    # 2. تنفيذ الخدمة
    summary, word_count = simple_summarize(input_text)
    
    # 3. تسجيل الاستخدام (الآن يُسجل كل استخدام كـ "مال حقيقي" لتغذية التقييم المستقبلي)
    try:
        record_api_usage(request.path, input_text, word_count)
    except Exception as e:
        # تسجيل فشل التوثيق إن حدث
        ees.record_and_hash_event("API_USE_FAIL", f"Error recording usage: {e}", "FAILURE")
        print(f"⚠️ تحذير: فشل تسجيل الاستخدام في REX-Ledger: {e}")
        
    # 4. إرجاع النتيجة
    response = {
        "summary": summary,
        "word_count_original": word_count,
        "status": "COMPLETED"
    }
    
    return jsonify(response)


@app.route('/ping', methods=['GET'])
def ping_service():
    """نقطة نهاية للتأكد من أن الـ API قيد التشغيل."""
    return jsonify({"status": "Operational", "project": "Zero_Cost_Monetizable_API"}), 200


if __name__ == '__main__':
    # لتشغيل الـ API محليًا (قابل للتوزيع لاحقًا على خدمة صفر تكلفة)
    print("--- AAL-CORE: بدأ تشغيل Zero-Cost Monetizable API (Flask) ---")
    # يتم تشغيل التطبيق في وضع التصحيح (Debug Mode) ليسهل عليك المتابعة
    app.run(debug=True)
    # Mandatory for PythonAnywhere
application = app