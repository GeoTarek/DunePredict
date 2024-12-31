from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from io import StringIO

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "*"}})

@app.route('/')
def index():
    return "مرحبا بك في واجهة التنبؤ بحركة الكثبان الرملية!"

@app.route('/predict', methods=['POST'])
def predict():
    if request.content_type != 'text/csv':
        return jsonify({"error": "نوع المحتوى غير مدعوم. يرجى إرسال ملف بصيغة CSV."}), 415

    try:
        csv_data = request.data.decode('utf-8')
        csv_data = csv_data.replace(';', ',')  # استبدال الفاصلة المنقوطة بالفاصلة العادية
        f = StringIO(csv_data)

        df = pd.read_csv(f)

        print("أسماء الأعمدة الموجودة في ملف CSV:", df.columns.tolist())

        required_columns = ['wind_speed', 'wind_direction', 'humidity', 'latitude', 'longitude', 'dune_movement_direction']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({"error": f"الأعمدة التالية مفقودة في ملف CSV: {missing_columns}"}), 400

        X = df[['wind_speed', 'wind_direction', 'humidity', 'latitude', 'longitude']]
        y = df['dune_movement_direction']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        results = []
        for idx, pred in enumerate(predictions):
            results.append({
                'id': idx + 1,
                'latitude': df.iloc[idx]['latitude'],
                'longitude': df.iloc[idx]['longitude'],
                'prediction': f"اتجاه الحركة: {pred:.2f} درجة"
            })

        return jsonify({'results': results})

    except Exception as e:
        print("خطأ:", str(e))
        return jsonify({"error": "حدث خطأ أثناء معالجة الملف. يرجى التحقق من التنسيق والمحاولة مرة أخرى.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
