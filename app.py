from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import json
import os
from werkzeug.utils import secure_filename
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable to store our dataset
pharmaceutical_data = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

def load_sample_data():
    """Load sample pharmaceutical data"""
    sample_data = {
        'drug_name': ['cetuximab', 'etanercept', 'urokinase', 'abciximab', 'hydrocortisone'],
        'side_effect_1': ['somnolence', 'dizziness', 'back pain', '', ''],
        'side_effect_2': ['headache', 'abdominal pain', 'fever', '', ''],
        'side_effect_3': ['cough', 'nausea', 'nausea', '', ''],
        'side_effect_4': ['renal failure', 'melanoma', '', '', ''],
        'side_effect_5': ['carcinoma', '', '', '', ''],
        'interacts_with_1': ['', '', '', '', 'butabarbital'],
        'interacts_with_2': ['', '', '', '', 'salsalate'],
        'interacts_with_3': ['', '', '', '', 'midodrine'],
        'disease_name': ['Adenocarcinoma', 'Asthma', 'Alzheimer disease', 'Complementary component deficiency', 'Asthma'],
        'disease_category': ['Cancer', 'Respiratory', 'Neurological', 'Immunological', 'Respiratory'],
        'drug_category': ['Antineoplastic agents', 'Antirheumatic agents', 'Thrombolytic agents', 'Anticoagulants', 'Anti-inflammatory agents'],
        'product_name': ['ERBITUX', 'ENBREL', 'Kinlytic', 'REOPRO', 'MyOxin'],
        'company_name': ['ImClone LLC', 'Immunex Corporation', 'ImaRx Therapeutics, Inc.', 'Eli Lilly and Company', 'GM Pharamceuticals, Inc'],
        'clinical_trial_title': ['Immune Response on Neoadjuvant Therapy in Non-small-cell Lung Cancer (NSCLC)', 
                               'Can We Miss Pigmented Lesions in Psoriasis Patients?',
                               '', 
                               'Efficacy Study on Early Versus Late Abciximab Administration During Primary Coronary Angioplasty',
                               'Low Doses Corticosteroids as Adjuvant Therapy for the Treatment of Severe H1N1 Flu'],
        'clinical_trial_participants': [41, 6, 0, 110, 40],
        'clinical_trial_status': ['Completed', 'Completed', '', 'Completed', 'Terminated']
    }
    return pd.DataFrame(sample_data)

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
            # Read the uploaded file
            if filename.endswith('.csv'):
                pharmaceutical_data = pd.read_csv(filepath)
            else:
                pharmaceutical_data = pd.read_excel(filepath)
            
            # Basic data info
            data_info = {
                'rows': len(pharmaceutical_data),
                'columns': len(pharmaceutical_data.columns),
                'column_names': pharmaceutical_data.columns.tolist()
            }
            
            return jsonify({
                'message': 'File uploaded successfully',
                'data_info': data_info
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/load_sample')
def load_sample():
    global pharmaceutical_data
    pharmaceutical_data = load_sample_data()
    
    data_info = {
        'rows': len(pharmaceutical_data),
        'columns': len(pharmaceutical_data.columns),
        'column_names': pharmaceutical_data.columns.tolist()
    }
    
    return jsonify({
        'message': 'Sample data loaded successfully',
        'data_info': data_info
    })

@app.route('/api/data')
def get_data():
    global pharmaceutical_data
    
    if pharmaceutical_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Calculate start and end indices
    start = (page - 1) * per_page
    end = start + per_page
    
    # Get subset of data
    data_subset = pharmaceutical_data.iloc[start:end]
    
    return jsonify({
        'data': data_subset.to_dict('records'),
        'total_rows': len(pharmaceutical_data),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(pharmaceutical_data) + per_page - 1) // per_page
    })

@app.route('/api/search')
def search_data():
    global pharmaceutical_data
    
    if pharmaceutical_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    query = request.args.get('query', '').lower()
    category = request.args.get('category', 'all')
    
    if not query:
        return jsonify({'data': pharmaceutical_data.to_dict('records')})
    
    # Search in specific columns based on category
    if category == 'drug':
        mask = pharmaceutical_data['drug_name'].str.lower().str.contains(query, na=False)
    elif category == 'disease':
        mask = pharmaceutical_data['disease_name'].str.lower().str.contains(query, na=False)
    elif category == 'company':
        mask = pharmaceutical_data['company_name'].str.lower().str.contains(query, na=False)
    else:  # Search all text columns
        mask = pharmaceutical_data.select_dtypes(include=['object']).apply(
            lambda x: x.str.lower().str.contains(query, na=False)
        ).any(axis=1)
    
    filtered_data = pharmaceutical_data[mask]
    
    return jsonify({
        'data': filtered_data.to_dict('records'),
        'total_results': len(filtered_data)
    })

@app.route('/api/analytics/drugs')
def drug_analytics():
    global pharmaceutical_data
    
    if pharmaceutical_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    try:
        # Drug category distribution
        drug_category_counts = pharmaceutical_data['drug_category'].value_counts()
        
        # Top companies by number of drugs
        company_counts = pharmaceutical_data['company_name'].value_counts().head(10)
        
        # Disease category distribution
        disease_category_counts = pharmaceutical_data['disease_category'].value_counts()
        
        return jsonify({
            'drug_categories': {
                'labels': drug_category_counts.index.tolist(),
                'values': drug_category_counts.values.tolist()
            },
            'top_companies': {
                'labels': company_counts.index.tolist(),
                'values': company_counts.values.tolist()
            },
            'disease_categories': {
                'labels': disease_category_counts.index.tolist(),
                'values': disease_category_counts.values.tolist()
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error generating analytics: {str(e)}'}), 500

@app.route('/api/analytics/clinical_trials')
def clinical_trial_analytics():
    global pharmaceutical_data
    
    if pharmaceutical_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    try:
        # Filter out rows with no clinical trial data
        trial_data = pharmaceutical_data[
            pharmaceutical_data['clinical_trial_title'].notna() & 
            (pharmaceutical_data['clinical_trial_title'] != '')
        ]
        
        if len(trial_data) == 0:
            return jsonify({'error': 'No clinical trial data available'}), 400
        
        # Clinical trial status distribution
        status_counts = trial_data['clinical_trial_status'].value_counts()
        
        # Participants by status
        participants_by_status = trial_data.groupby('clinical_trial_status')['clinical_trial_participants'].sum()
        
        return jsonify({
            'trial_status': {
                'labels': status_counts.index.tolist(),
                'values': status_counts.values.tolist()
            },
            'participants_by_status': {
                'labels': participants_by_status.index.tolist(),
                'values': participants_by_status.values.tolist()
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error generating clinical trial analytics: {str(e)}'}), 500

@app.route('/api/analytics/side_effects')
def side_effect_analytics():
    global pharmaceutical_data
    
    if pharmaceutical_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    try:
        # Collect all side effects
        side_effects = []
        for col in pharmaceutical_data.columns:
            if 'side_effect' in col.lower():
                effects = pharmaceutical_data[col].dropna()
                effects = effects[effects != '']
                side_effects.extend(effects.tolist())
        
        if not side_effects:
            return jsonify({'error': 'No side effect data available'}), 400
        
        # Count side effects
        side_effect_series = pd.Series(side_effects)
        top_side_effects = side_effect_series.value_counts().head(15)
        
        return jsonify({
            'top_side_effects': {
                'labels': top_side_effects.index.tolist(),
                'values': top_side_effects.values.tolist()
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error generating side effect analytics: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)