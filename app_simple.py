from flask import Flask, render_template, request, jsonify
import csv
import json
import os
from werkzeug.utils import secure_filename
from collections import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable to store our dataset
pharmaceutical_data = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def load_sample_data():
    """Load sample pharmaceutical data"""
    sample_data = [
        {
            'drug_name': 'cetuximab',
            'side_effect_1': 'somnolence',
            'side_effect_2': 'headache',
            'side_effect_3': 'cough',
            'side_effect_4': 'renal failure',
            'side_effect_5': 'carcinoma',
            'interacts_with_1': '',
            'interacts_with_2': '',
            'interacts_with_3': '',
            'disease_name': 'Adenocarcinoma',
            'disease_category': 'Cancer',
            'drug_category': 'Antineoplastic agents',
            'product_name': 'ERBITUX',
            'company_name': 'ImClone LLC',
            'clinical_trial_title': 'Immune Response on Neoadjuvant Therapy in Non-small-cell Lung Cancer (NSCLC)',
            'clinical_trial_participants': 41,
            'clinical_trial_status': 'Completed'
        },
        {
            'drug_name': 'etanercept',
            'side_effect_1': 'dizziness',
            'side_effect_2': 'abdominal pain',
            'side_effect_3': 'nausea',
            'side_effect_4': 'melanoma',
            'side_effect_5': '',
            'interacts_with_1': '',
            'interacts_with_2': '',
            'interacts_with_3': '',
            'disease_name': 'Asthma',
            'disease_category': 'Respiratory',
            'drug_category': 'Antirheumatic agents',
            'product_name': 'ENBREL',
            'company_name': 'Immunex Corporation',
            'clinical_trial_title': 'Can We Miss Pigmented Lesions in Psoriasis Patients?',
            'clinical_trial_participants': 6,
            'clinical_trial_status': 'Completed'
        },
        {
            'drug_name': 'urokinase',
            'side_effect_1': 'back pain',
            'side_effect_2': 'fever',
            'side_effect_3': 'nausea',
            'side_effect_4': '',
            'side_effect_5': '',
            'interacts_with_1': '',
            'interacts_with_2': '',
            'interacts_with_3': '',
            'disease_name': 'Alzheimer disease',
            'disease_category': 'Neurological',
            'drug_category': 'Thrombolytic agents',
            'product_name': 'Kinlytic',
            'company_name': 'ImaRx Therapeutics, Inc.',
            'clinical_trial_title': '',
            'clinical_trial_participants': 0,
            'clinical_trial_status': ''
        },
        {
            'drug_name': 'abciximab',
            'side_effect_1': '',
            'side_effect_2': '',
            'side_effect_3': '',
            'side_effect_4': '',
            'side_effect_5': '',
            'interacts_with_1': '',
            'interacts_with_2': '',
            'interacts_with_3': '',
            'disease_name': 'Complementary component deficiency',
            'disease_category': 'Immunological',
            'drug_category': 'Anticoagulants',
            'product_name': 'REOPRO',
            'company_name': 'Eli Lilly and Company',
            'clinical_trial_title': 'Efficacy Study on Early Versus Late Abciximab Administration During Primary Coronary Angioplasty',
            'clinical_trial_participants': 110,
            'clinical_trial_status': 'Completed'
        },
        {
            'drug_name': 'hydrocortisone',
            'side_effect_1': '',
            'side_effect_2': '',
            'side_effect_3': '',
            'side_effect_4': '',
            'side_effect_5': '',
            'interacts_with_1': 'butabarbital',
            'interacts_with_2': 'salsalate',
            'interacts_with_3': 'midodrine',
            'disease_name': 'Asthma',
            'disease_category': 'Respiratory',
            'drug_category': 'Anti-inflammatory agents',
            'product_name': 'MyOxin',
            'company_name': 'GM Pharamceuticals, Inc',
            'clinical_trial_title': 'Low Doses Corticosteroids as Adjuvant Therapy for the Treatment of Severe H1N1 Flu',
            'clinical_trial_participants': 40,
            'clinical_trial_status': 'Terminated'
        }
    ]
    return sample_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global pharmaceutical_data
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read the uploaded CSV file
            pharmaceutical_data = []
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    pharmaceutical_data.append(dict(row))
            
            # Basic data info
            data_info = {
                'rows': len(pharmaceutical_data),
                'columns': len(pharmaceutical_data[0].keys()) if pharmaceutical_data else 0,
                'column_names': list(pharmaceutical_data[0].keys()) if pharmaceutical_data else []
            }
            
            return jsonify({
                'message': 'File uploaded successfully',
                'data_info': data_info
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400

@app.route('/load_sample')
def load_sample():
    global pharmaceutical_data
    pharmaceutical_data = load_sample_data()
    
    data_info = {
        'rows': len(pharmaceutical_data),
        'columns': len(pharmaceutical_data[0].keys()) if pharmaceutical_data else 0,
        'column_names': list(pharmaceutical_data[0].keys()) if pharmaceutical_data else []
    }
    
    return jsonify({
        'message': 'Sample data loaded successfully',
        'data_info': data_info
    })

@app.route('/api/data')
def get_data():
    global pharmaceutical_data
    
    if not pharmaceutical_data:
        return jsonify({'error': 'No data loaded'}), 400
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Calculate start and end indices
    start = (page - 1) * per_page
    end = start + per_page
    
    # Get subset of data
    data_subset = pharmaceutical_data[start:end]
    
    total_pages = (len(pharmaceutical_data) + per_page - 1) // per_page
    
    return jsonify({
        'data': data_subset,
        'total_rows': len(pharmaceutical_data),
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    })

@app.route('/api/search')
def search_data():
    global pharmaceutical_data
    
    if not pharmaceutical_data:
        return jsonify({'error': 'No data loaded'}), 400
    
    query = request.args.get('query', '').lower()
    category = request.args.get('category', 'all')
    
    if not query:
        return jsonify({'data': pharmaceutical_data})
    
    filtered_data = []
    
    for row in pharmaceutical_data:
        match = False
        
        if category == 'drug':
            if query in str(row.get('drug_name', '')).lower():
                match = True
        elif category == 'disease':
            if query in str(row.get('disease_name', '')).lower():
                match = True
        elif category == 'company':
            if query in str(row.get('company_name', '')).lower():
                match = True
        else:  # Search all fields
            for value in row.values():
                if query in str(value).lower():
                    match = True
                    break
        
        if match:
            filtered_data.append(row)
    
    return jsonify({
        'data': filtered_data,
        'total_results': len(filtered_data)
    })

@app.route('/api/analytics/drugs')
def drug_analytics():
    global pharmaceutical_data
    
    if not pharmaceutical_data:
        return jsonify({'error': 'No data loaded'}), 400
    
    try:
        # Drug category distribution
        drug_categories = [row.get('drug_category', '') for row in pharmaceutical_data if row.get('drug_category')]
        drug_category_counts = Counter(drug_categories)
        
        # Top companies by number of drugs
        companies = [row.get('company_name', '') for row in pharmaceutical_data if row.get('company_name')]
        company_counts = Counter(companies)
        top_companies = dict(company_counts.most_common(10))
        
        # Disease category distribution
        disease_categories = [row.get('disease_category', '') for row in pharmaceutical_data if row.get('disease_category')]
        disease_category_counts = Counter(disease_categories)
        
        return jsonify({
            'drug_categories': {
                'labels': list(drug_category_counts.keys()),
                'values': list(drug_category_counts.values())
            },
            'top_companies': {
                'labels': list(top_companies.keys()),
                'values': list(top_companies.values())
            },
            'disease_categories': {
                'labels': list(disease_category_counts.keys()),
                'values': list(disease_category_counts.values())
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error generating analytics: {str(e)}'}), 500

@app.route('/api/analytics/clinical_trials')
def clinical_trial_analytics():
    global pharmaceutical_data
    
    if not pharmaceutical_data:
        return jsonify({'error': 'No data loaded'}), 400
    
    try:
        # Filter out rows with no clinical trial data
        trial_data = [row for row in pharmaceutical_data if row.get('clinical_trial_title', '').strip()]
        
        if not trial_data:
            return jsonify({'error': 'No clinical trial data available'}), 400
        
        # Clinical trial status distribution
        statuses = [row.get('clinical_trial_status', '') for row in trial_data if row.get('clinical_trial_status')]
        status_counts = Counter(statuses)
        
        # Participants by status
        participants_by_status = {}
        for row in trial_data:
            status = row.get('clinical_trial_status', '')
            participants = int(row.get('clinical_trial_participants', 0) or 0)
            if status:
                participants_by_status[status] = participants_by_status.get(status, 0) + participants
        
        return jsonify({
            'trial_status': {
                'labels': list(status_counts.keys()),
                'values': list(status_counts.values())
            },
            'participants_by_status': {
                'labels': list(participants_by_status.keys()),
                'values': list(participants_by_status.values())
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error generating clinical trial analytics: {str(e)}'}), 500

@app.route('/api/analytics/side_effects')
def side_effect_analytics():
    global pharmaceutical_data
    
    if not pharmaceutical_data:
        return jsonify({'error': 'No data loaded'}), 400
    
    try:
        # Collect all side effects
        side_effects = []
        for row in pharmaceutical_data:
            for i in range(1, 6):  # side_effect_1 to side_effect_5
                effect = row.get(f'side_effect_{i}', '')
                if effect and effect.strip():
                    side_effects.append(effect.strip())
        
        if not side_effects:
            return jsonify({'error': 'No side effect data available'}), 400
        
        # Count side effects
        side_effect_counts = Counter(side_effects)
        top_side_effects = dict(side_effect_counts.most_common(15))
        
        return jsonify({
            'top_side_effects': {
                'labels': list(top_side_effects.keys()),
                'values': list(top_side_effects.values())
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error generating side effect analytics: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)