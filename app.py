"""
Database System Project-1: Normalization and ER Diagram Generator
Main Flask Application

This is the main web application that integrates all database modules
and provides a user-friendly interface for CSV upload, FD detection,
normalization, and ER diagram generation.
"""

import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import json
import traceback

# Import our database modules
from database.fd_detection import FunctionalDependencyDetector
from database.normalization import NormalizationEngine
from database.decomposition import DecompositionChecker
from database.schema_generator import SchemaGenerator

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and export directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('exports', exist_ok=True)

# Global variables to store analysis results
analysis_results = {}

@app.route('/')
def index():
    """Main page with file upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and initial processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Please upload a CSV file'}), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read and validate CSV
        try:
            data = pd.read_csv(filepath)
            
            # Basic validation
            if data.empty:
                return jsonify({'error': 'CSV file is empty'}), 400
            
            if len(data.columns) < 2:
                return jsonify({'error': 'CSV must have at least 2 columns'}), 400
            
            # Clean column names
            data.columns = data.columns.str.strip()
            
            # Remove rows with all NaN values
            data = data.dropna(how='all')
            
            # Store basic file information
            file_info = {
                'filename': filename,
                'filepath': filepath,
                'rows': len(data),
                'columns': len(data.columns),
                'attributes': list(data.columns),
                'sample_data': data.head().to_dict('records')
            }
            
            # Store data globally for further processing
            analysis_results['data'] = data
            analysis_results['file_info'] = file_info
            
            return jsonify({
                'success': True,
                'file_info': file_info,
                'message': 'File uploaded successfully'
            })
            
        except Exception as e:
            return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload error: {str(e)}'}), 500

@app.route('/analyze', methods=['POST'])
def analyze_data():
    """Analyze the uploaded data for functional dependencies."""
    try:
        if 'data' not in analysis_results:
            return jsonify({'error': 'No data uploaded'}), 400
        
        data = analysis_results['data']
        
        # Phase 1: Functional Dependency Detection
        fd_detector = FunctionalDependencyDetector(data)
        functional_dependencies = fd_detector.detect_functional_dependencies()
        candidate_keys = fd_detector.find_candidate_keys()
        
        # Get FD summary
        fd_summary = fd_detector.get_fd_summary()
        
        # Phase 2: Normalization Analysis
        normalization_engine = NormalizationEngine(data, functional_dependencies, candidate_keys)
        current_nf = normalization_engine.check_normal_form()
        normalization_summary = normalization_engine.get_normalization_summary()
        
        # Phase 3: Generate normalized relations
        relations_3nf = normalization_engine.normalize_to_3nf()
        relations_bcnf = normalization_engine.normalize_to_bcnf()
        
        # Phase 4: Check decomposition quality
        decomposition_checker = DecompositionChecker(data, functional_dependencies)
        decomposition_3nf = decomposition_checker.get_decomposition_summary(relations_3nf)
        decomposition_bcnf = decomposition_checker.get_decomposition_summary(relations_bcnf)
        
        # Store analysis results
        analysis_results.update({
            'functional_dependencies': functional_dependencies,
            'candidate_keys': candidate_keys,
            'fd_summary': fd_summary,
            'current_normal_form': current_nf,
            'normalization_summary': normalization_summary,
            'relations_3nf': relations_3nf,
            'relations_bcnf': relations_bcnf,
            'decomposition_3nf': decomposition_3nf,
            'decomposition_bcnf': decomposition_bcnf
        })
        
        return jsonify({
            'success': True,
            'results': {
                'fd_summary': fd_summary,
                'current_normal_form': current_nf,
                'normalization_summary': normalization_summary,
                'decomposition_3nf': decomposition_3nf,
                'decomposition_bcnf': decomposition_bcnf
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

@app.route('/generate_schema', methods=['POST'])
def generate_schema():
    """Generate relational schema and ER diagram."""
    try:
        if 'relations_3nf' not in analysis_results:
            return jsonify({'error': 'No analysis results available'}), 400
        
        # Get normalization type from request
        normalization_type = request.json.get('type', '3nf')
        
        if normalization_type == 'bcnf':
            relations = analysis_results['relations_bcnf']
        else:
            relations = analysis_results['relations_3nf']
        
        # Phase 5: Schema Generation
        schema_generator = SchemaGenerator(
            relations,
            analysis_results['functional_dependencies'],
            analysis_results['candidate_keys']
        )
        
        # Generate relational schema
        relational_schema = schema_generator.generate_relational_schema()
        
        # Generate ER diagram
        er_diagram = schema_generator.generate_er_diagram(
            output_path=f'exports/er_diagram_{normalization_type}'
        )
        
        # Export SQL schema
        sql_file = schema_generator.export_sql_schema(
            output_path=f'exports/schema_{normalization_type}.sql'
        )
        
        # Get schema summary
        schema_summary = schema_generator.get_schema_summary()
        
        # Store schema results
        analysis_results.update({
            f'relational_schema_{normalization_type}': relational_schema,
            f'er_diagram_{normalization_type}': er_diagram,
            f'schema_summary_{normalization_type}': schema_summary,
            f'sql_file_{normalization_type}': sql_file
        })
        
        return jsonify({
            'success': True,
            'schema': {
                'relational_schema': relational_schema,
                'er_diagram': er_diagram,
                'schema_summary': schema_summary,
                'sql_file': sql_file
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Schema generation error: {str(e)}'}), 500

@app.route('/results')
def results():
    """Display analysis results page."""
    if 'data' not in analysis_results:
        flash('No data available. Please upload a CSV file first.', 'error')
        return redirect(url_for('index'))
    
    return render_template('results.html', results=analysis_results)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated files."""
    try:
        file_path = os.path.join('exports', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/api/relations/<normalization_type>')
def get_relations(normalization_type):
    """Get relations for a specific normalization type."""
    try:
        key = f'relations_{normalization_type}'
        if key not in analysis_results:
            return jsonify({'error': 'Relations not found'}), 404
        
        relations = analysis_results[key]
        
        # Convert DataFrames to dictionaries for JSON serialization
        serialized_relations = []
        for relation in relations:
            serialized_relation = {
                'name': relation['name'],
                'attributes': relation['attributes'],
                'primary_key': relation.get('primary_key', []),
                'data': relation['data'].to_dict('records'),
                'tuple_count': len(relation['data'])
            }
            serialized_relations.append(serialized_relation)
        
        return jsonify({
            'success': True,
            'relations': serialized_relations
        })
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving relations: {str(e)}'}), 500

@app.route('/api/fd_details')
def get_fd_details():
    """Get detailed functional dependency information."""
    try:
        if 'fd_summary' not in analysis_results:
            return jsonify({'error': 'No FD analysis available'}), 404
        
        return jsonify({
            'success': True,
            'fd_details': analysis_results['fd_summary']
        })
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving FD details: {str(e)}'}), 500

@app.route('/api/schema_comparison')
def schema_comparison():
    """Compare different normalization approaches."""
    try:
        comparison = {
            'original': {
                'attributes': len(analysis_results['data'].columns),
                'tuples': len(analysis_results['data']),
                'normal_form': analysis_results.get('current_normal_form', 'Unknown')
            }
        }
        
        # Add 3NF comparison if available
        if 'relations_3nf' in analysis_results:
            relations_3nf = analysis_results['relations_3nf']
            comparison['3nf'] = {
                'relations': len(relations_3nf),
                'total_tuples': sum(len(r['data']) for r in relations_3nf),
                'avg_attributes': sum(len(r['attributes']) for r in relations_3nf) / len(relations_3nf)
            }
        
        # Add BCNF comparison if available
        if 'relations_bcnf' in analysis_results:
            relations_bcnf = analysis_results['relations_bcnf']
            comparison['bcnf'] = {
                'relations': len(relations_bcnf),
                'total_tuples': sum(len(r['data']) for r in relations_bcnf),
                'avg_attributes': sum(len(r['attributes']) for r in relations_bcnf) / len(relations_bcnf)
            }
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
        
    except Exception as e:
        return jsonify({'error': f'Error in schema comparison: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("Starting Database Normalization and ER Diagram Generator...")
    print("Open your browser and go to http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)