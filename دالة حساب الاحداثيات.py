from flask import Flask, request, jsonify
from flask_cors import CORS  # استيراد flask-cors
import math

app = Flask(__name__)

# تفعيل CORS للمسار '/calculate' مع السماح لجميع الأصول
CORS(app, resources={r"/calculate": {"origins": "*"}})

# لتخزين المدخلات والنتائج في ذاكرة الخادم
entries = []

# دالة لحساب المسافة بناءً على سرعة الرياح والزمن
def calculate_distance(speed, time):
    return speed * time

# دالة لحساب الإحداثيات الجديدة بناءً على الإحداثيات الأصلية، الاتجاه، والمسافة
def calculate_new_coordinates(latitude, longitude, direction, distance_km):
    # تحويل الدرجات إلى راديان
    direction_rad = math.radians(direction)
    latitude_rad = math.radians(latitude)
    longitude_rad = math.radians(longitude)

    # نصف قطر الأرض بالكيلومترات
    earth_radius = 6371.0

    # حساب خطوط العرض والطول الجديدة
    new_latitude_rad = math.asin(
        math.sin(latitude_rad) * math.cos(distance_km / earth_radius) +
        math.cos(latitude_rad) * math.sin(distance_km / earth_radius) * math.cos(direction_rad)
    )

    new_longitude_rad = longitude_rad + math.atan2(
        math.sin(direction_rad) * math.sin(distance_km / earth_radius) * math.cos(latitude_rad),
        math.cos(distance_km / earth_radius) - math.sin(latitude_rad) * math.sin(new_latitude_rad)
    )

    # تحويل النتائج إلى درجات
    new_latitude = math.degrees(new_latitude_rad)
    new_longitude = math.degrees(new_longitude_rad)

    return new_latitude, new_longitude

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()

    latitude = data['latitude']
    longitude = data['longitude']
    direction = data['direction']
    windspeed = data['windspeed']
    time = data['time']

    # حساب المسافة
    distance_km = calculate_distance(windspeed, time)

    # حساب الإحداثيات الجديدة
    new_latitude, new_longitude = calculate_new_coordinates(latitude, longitude, direction, distance_km)

    new_latitude = round(new_latitude, 3)
    new_longitude = round(new_longitude, 3)

    # إنشاء ID مميز
    result_id = f"id_{latitude}_{longitude}"

    # تخزين المدخلات في الذاكرة (من أجل تتبع البيانات السابقة)
    entries.append({
        'id': result_id,
        'latitude': latitude,
        'longitude': longitude,
        'direction': direction,
        'windspeed': windspeed,
        'time': time,
        'new_latitude': new_latitude,
        'new_longitude': new_longitude
    })

    # إرجاع الإحداثيات الجديدة مع ID
    return jsonify({
        'id': result_id,
        'new_latitude': new_latitude,
        'new_longitude': new_longitude,
        'entries': entries  # إرجاع جميع المدخلات (إذا كنت بحاجة إلى هذه البيانات)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6060)
