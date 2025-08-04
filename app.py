"""
Database System Project-1: Normalization and ER Diagram Generator
Main Flask Application - Enhanced for Large Pharmaceutical Datasets

This is the main web application that integrates all database modules
and provides a user-friendly interface for CSV upload, FD detection,
normalization, and ER diagram generation.
"""

import os
import pandas as pd
import dask.dataframe as dd
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import json
import traceback
import psutil
from tqdm import tqdm
import time
import gc

# Import our database modules
from database.fd_detection import FunctionalDependencyDetector
from database.normalization import NormalizationEngine
from database.decomposition import DecompositionChecker
from database.schema_generator import SchemaGenerator

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size for large datasets
app.config['CHUNK_SIZE'] = 10000  # Process data in chunks for large files

# Ensure upload and export directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('exports', exist_ok=True)

# Global variables to store analysis results
analysis_results = {}

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def validate_pharmaceutical_data(data):
    """
    Validate pharmaceutical data structure and content.
    
    Args:
        data: pandas DataFrame
        
    Returns:
        dict: Validation results with warnings and suggestions
    """
    validation_results = {
        'warnings': [],
        'suggestions': [],
        'data_quality': 'good'
    }
    
    # Check for pharmaceutical-specific columns
    expected_pharma_columns = [
        'drug name', 'drug_name', 'medication', 'product name', 'product_name',
        'side effect', 'adverse_effect', 'company name', 'company_name',
        'disease', 'condition', 'clinical trial', 'trial'
    ]
    
    pharma_columns_found = []
    for col in data.columns:
        col_lower = col.lower().strip()
        for expected in expected_pharma_columns:
            if expected in col_lower:
                pharma_columns_found.append(col)
                break
    
    if len(pharma_columns_found) < 3:
        validation_results['warnings'].append(
            "This doesn't appear to be pharmaceutical data. "
            "Expected columns like 'drug name', 'side effect', 'disease', etc."
        )
    
    # Check for duplicate column names (common in pharmaceutical datasets)
    duplicate_columns = []
    column_counts = {}
    for col in data.columns:
        cleaned_col = col.strip().lower()
        if cleaned_col in column_counts:
            column_counts[cleaned_col] += 1
            duplicate_columns.append(col)
        else:
            column_counts[cleaned_col] = 1
    
    if duplicate_columns:
        validation_results['warnings'].append(
            f"Found duplicate column names: {', '.join(duplicate_columns)}. "
            "These will be automatically renamed with suffixes."
        )
    
    # Check for high percentage of missing values
    missing_percentages = data.isnull().sum() / len(data) * 100
    high_missing_cols = missing_percentages[missing_percentages > 50].index.tolist()
    
    if high_missing_cols:
        validation_results['warnings'].append(
            f"Columns with >50% missing data: {', '.join(high_missing_cols)}. "
            "Consider data cleaning or removal of these columns."
        )
    
    # Check data size for performance warnings
    memory_mb = data.memory_usage(deep=True).sum() / 1024 / 1024
    if memory_mb > 100:
        validation_results['suggestions'].append(
            f"Large dataset detected ({memory_mb:.1f}MB). "
            "Processing may take longer. Consider using chunked processing."
        )
    
    if len(data) > 50000:
        validation_results['suggestions'].append(
            f"Large number of rows ({len(data):,}). "
            "Functional dependency detection may be time-consuming."
        )
    
    return validation_results

def clean_pharmaceutical_data(data):
    """
    Clean and preprocess pharmaceutical data.
    
    Args:
        data: pandas DataFrame
        
    Returns:
        pandas DataFrame: Cleaned data
    """
    # Make a copy to avoid modifying original
    cleaned_data = data.copy()
    
    # Handle duplicate column names
    columns = []
    column_counts = {}
    
    for col in cleaned_data.columns:
        cleaned_col = col.strip()
        if cleaned_col in column_counts:
            column_counts[cleaned_col] += 1
            new_col = f"{cleaned_col}_{column_counts[cleaned_col]}"
        else:
            column_counts[cleaned_col] = 1
            new_col = cleaned_col
        columns.append(new_col)
    
    cleaned_data.columns = columns
    
    # Remove completely empty rows
    cleaned_data = cleaned_data.dropna(how='all')
    
    # Fill empty cells with 'NULL' for better FD detection
    cleaned_data = cleaned_data.fillna('NULL')
    
    # Clean text data - remove extra whitespace
    for col in cleaned_data.select_dtypes(include=['object']).columns:
        cleaned_data[col] = cleaned_data[col].astype(str).str.strip()
    
    return cleaned_data

@app.route('/')
def index():
    """Main page with file upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and initial processing with large file support."""
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
        
        # Get file size for processing decisions
        file_size_mb = os.path.getsize(filepath) / 1024 / 1024
        
        # Read and validate CSV with appropriate method
        try:
            if file_size_mb > 100:  # Use Dask for large files
                print(f"Large file detected ({file_size_mb:.1f}MB), using Dask for processing...")
                # Read with Dask for memory efficiency
                dask_df = dd.read_csv(filepath)
                # Convert to pandas for a sample
                data = dask_df.head(10000).compute()  # Sample first 10k rows for analysis
                total_rows = len(dask_df)  # This is computed efficiently
            else:
                data = pd.read_csv(filepath)
                total_rows = len(data)
            
            # Basic validation
            if data.empty:
                return jsonify({'error': 'CSV file is empty'}), 400
            
            if len(data.columns) < 2:
                return jsonify({'error': 'CSV must have at least 2 columns'}), 400
            
            # Validate pharmaceutical data structure
            validation_results = validate_pharmaceutical_data(data)
            
            # Clean the data
            cleaned_data = clean_pharmaceutical_data(data)
            
            # Store basic file information
            file_info = {
                'filename': filename,
                'filepath': filepath,
                'file_size_mb': file_size_mb,
                'rows': len(cleaned_data),
                'total_rows': total_rows,
                'columns': len(cleaned_data.columns),
                'attributes': list(cleaned_data.columns),
                'sample_data': cleaned_data.head(10).to_dict('records'),
                'validation': validation_results,
                'memory_usage_mb': get_memory_usage(),
                'is_large_dataset': file_size_mb > 50,
                'processing_method': 'dask' if file_size_mb > 100 else 'pandas'
            }
            
            # Store data globally for further processing
            analysis_results['data'] = cleaned_data
            analysis_results['file_info'] = file_info
            analysis_results['original_file_path'] = filepath
            
            return jsonify({
                'success': True,
                'file_info': file_info,
                'message': 'File uploaded and validated successfully'
            })
            
        except Exception as e:
            return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload error: {str(e)}'}), 500

@app.route('/analyze', methods=['POST'])
def analyze_data():
    """Analyze the uploaded data for functional dependencies with progress tracking."""
    try:
        if 'data' not in analysis_results:
            return jsonify({'error': 'No data uploaded'}), 400
        
        data = analysis_results['data']
        file_info = analysis_results['file_info']
        
        # For very large datasets, limit analysis to improve performance
        if len(data) > 5000:
            sample_data = data.sample(n=5000, random_state=42)
            analysis_note = f"Analysis performed on sample of 5,000 rows from {len(data):,} total rows"
        else:
            sample_data = data
            analysis_note = f"Analysis performed on all {len(data):,} rows"
        
        print(f"Starting analysis on {len(sample_data)} rows...")
        start_time = time.time()
        
        # Phase 1: Functional Dependency Detection
        print("Phase 1: Detecting functional dependencies...")
        fd_detector = FunctionalDependencyDetector(sample_data)
        functional_dependencies = fd_detector.detect_functional_dependencies()
        candidate_keys = fd_detector.find_candidate_keys()
        
        # Get FD summary
        fd_summary = fd_detector.get_fd_summary()
        fd_summary['analysis_note'] = analysis_note
        
        # Phase 2: Normalization Analysis
        print("Phase 2: Analyzing normalization opportunities...")
        normalization_engine = NormalizationEngine(sample_data, functional_dependencies, candidate_keys)
        current_nf = normalization_engine.check_normal_form()
        normalization_summary = normalization_engine.get_normalization_summary()
        
        # Phase 3: Generate normalized relations
        print("Phase 3: Generating normalized relations...")
        relations_3nf = normalization_engine.normalize_to_3nf()
        relations_bcnf = normalization_engine.normalize_to_bcnf()
        
        # Phase 4: Check decomposition quality
        print("Phase 4: Checking decomposition quality...")
        decomposition_checker = DecompositionChecker(sample_data, functional_dependencies)
        decomposition_3nf = decomposition_checker.get_decomposition_summary(relations_3nf)
        decomposition_bcnf = decomposition_checker.get_decomposition_summary(relations_bcnf)
        
        analysis_time = time.time() - start_time
        
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
            'decomposition_bcnf': decomposition_bcnf,
            'analysis_time': analysis_time,
            'memory_usage_after_analysis': get_memory_usage(),
            'sample_used': len(sample_data) < len(data)
        })
        
        # Force garbage collection for large datasets
        if file_info.get('is_large_dataset', False):
            gc.collect()
        
        print(f"Analysis completed in {analysis_time:.2f} seconds")
        
        return jsonify({
            'success': True,
            'results': {
                'fd_summary': fd_summary,
                'current_normal_form': current_nf,
                'normalization_summary': normalization_summary,
                'decomposition_3nf': decomposition_3nf,
                'decomposition_bcnf': decomposition_bcnf,
                'analysis_time': analysis_time,
                'memory_usage_mb': get_memory_usage()
            }
        })
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

@app.route('/generate_schema', methods=['POST'])
def generate_schema():
    """Generate relational schema and ER diagram with pharmaceutical optimizations."""
    try:
        if 'relations_3nf' not in analysis_results:
            return jsonify({'error': 'No analysis results available'}), 400
        
        # Get normalization type from request
        normalization_type = request.json.get('type', '3nf')
        
        if normalization_type == 'bcnf':
            relations = analysis_results['relations_bcnf']
        else:
            relations = analysis_results['relations_3nf']
        
        print(f"Generating schema for {normalization_type.upper()} normalization...")
        start_time = time.time()
        
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
        
        # Export Excel file for pharmaceutical data
        excel_file = f'exports/pharmaceutical_analysis_{normalization_type}.xlsx'
        export_to_excel(relations, excel_file, normalization_type)
        
        # Get schema summary
        schema_summary = schema_generator.get_schema_summary()
        schema_summary['excel_export'] = excel_file
        
        generation_time = time.time() - start_time
        
        # Store schema results
        analysis_results.update({
            f'relational_schema_{normalization_type}': relational_schema,
            f'er_diagram_{normalization_type}': er_diagram,
            f'schema_summary_{normalization_type}': schema_summary,
            f'sql_file_{normalization_type}': sql_file,
            f'excel_file_{normalization_type}': excel_file,
            f'generation_time_{normalization_type}': generation_time
        })
        
        print(f"Schema generation completed in {generation_time:.2f} seconds")
        
        return jsonify({
            'success': True,
            'schema': {
                'relational_schema': relational_schema,
                'er_diagram': er_diagram,
                'schema_summary': schema_summary,
                'sql_file': sql_file,
                'excel_file': excel_file,
                'generation_time': generation_time
            }
        })
        
    except Exception as e:
        print(f"Schema generation error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Schema generation error: {str(e)}'}), 500

def export_to_excel(relations, excel_file, normalization_type):
    """Export pharmaceutical analysis results to Excel format."""
    try:
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            # Summary sheet
            summary_data = []
            for i, relation in enumerate(relations):
                summary_data.append({
                    'Relation': relation['name'],
                    'Attributes': ', '.join(relation['attributes']),
                    'Primary Key': ', '.join(relation.get('primary_key', [])),
                    'Tuple Count': len(relation['data']),
                    'Normalization': normalization_type.upper()
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Individual relation sheets
            for relation in relations:
                sheet_name = relation['name'][:31]  # Excel sheet name limit
                relation['data'].to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Analysis metadata
            if 'file_info' in analysis_results:
                metadata = {
                    'Original File': [analysis_results['file_info']['filename']],
                    'Total Rows': [analysis_results['file_info']['total_rows']],
                    'Total Columns': [analysis_results['file_info']['columns']],
                    'File Size (MB)': [analysis_results['file_info']['file_size_mb']],
                    'Processing Method': [analysis_results['file_info']['processing_method']],
                    'Analysis Time (s)': [analysis_results.get('analysis_time', 'N/A')],
                    'Memory Usage (MB)': [analysis_results.get('memory_usage_after_analysis', 'N/A')]
                }
                metadata_df = pd.DataFrame(metadata)
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
    except Exception as e:
        print(f"Excel export error: {str(e)}")
        # Don't fail the whole operation if Excel export fails
        pass

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

@app.route('/api/dataset_stats')
def dataset_stats():
    """Get detailed statistics about the uploaded dataset."""
    try:
        if 'data' not in analysis_results:
            return jsonify({'error': 'No dataset available'}), 404
        
        data = analysis_results['data']
        file_info = analysis_results['file_info']
        
        # Calculate detailed statistics
        stats = {
            'basic_info': {
                'filename': file_info['filename'],
                'total_rows': file_info['total_rows'],
                'sampled_rows': len(data),
                'columns': len(data.columns),
                'file_size_mb': file_info['file_size_mb'],
                'memory_usage_mb': file_info['memory_usage_mb']
            },
            'data_quality': {
                'missing_values': data.isnull().sum().to_dict(),
                'missing_percentages': (data.isnull().sum() / len(data) * 100).to_dict(),
                'duplicate_rows': data.duplicated().sum(),
                'unique_values_per_column': data.nunique().to_dict()
            },
            'column_types': data.dtypes.apply(str).to_dict(),
            'validation_results': file_info.get('validation', {}),
            'processing_info': {
                'processing_method': file_info['processing_method'],
                'is_large_dataset': file_info['is_large_dataset'],
                'sample_used': analysis_results.get('sample_used', False)
            }
        }
        
        # Add analysis timing if available
        if 'analysis_time' in analysis_results:
            stats['performance'] = {
                'analysis_time_seconds': analysis_results['analysis_time'],
                'memory_after_analysis_mb': analysis_results.get('memory_usage_after_analysis', 'N/A')
            }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting dataset stats: {str(e)}'}), 500

@app.route('/api/pharmaceutical_insights')
def pharmaceutical_insights():
    """Get pharmaceutical-specific insights from the data."""
    try:
        if 'data' not in analysis_results:
            return jsonify({'error': 'No dataset available'}), 404
        
        data = analysis_results['data']
        insights = {
            'drug_analysis': {},
            'side_effects': {},
            'clinical_trials': {},
            'companies': {}
        }
        
        # Find pharmaceutical-related columns
        drug_cols = [col for col in data.columns if any(term in col.lower() for term in ['drug', 'medication', 'product'])]
        side_effect_cols = [col for col in data.columns if 'side effect' in col.lower()]
        company_cols = [col for col in data.columns if 'company' in col.lower()]
        trial_cols = [col for col in data.columns if 'trial' in col.lower()]
        
        # Drug analysis
        if drug_cols:
            main_drug_col = drug_cols[0]
            unique_drugs = data[main_drug_col].value_counts()
            insights['drug_analysis'] = {
                'total_unique_drugs': len(unique_drugs),
                'most_common_drugs': unique_drugs.head(10).to_dict(),
                'drugs_with_single_entry': sum(unique_drugs == 1)
            }
        
        # Side effects analysis
        if side_effect_cols:
            all_side_effects = []
            for col in side_effect_cols:
                effects = data[col].dropna()
                effects = effects[effects != 'NULL']
                all_side_effects.extend(effects.tolist())
            
            if all_side_effects:
                side_effect_counts = pd.Series(all_side_effects).value_counts()
                insights['side_effects'] = {
                    'total_side_effects_reported': len(all_side_effects),
                    'unique_side_effects': len(side_effect_counts),
                    'most_common_side_effects': side_effect_counts.head(10).to_dict()
                }
        
        # Company analysis
        if company_cols:
            main_company_col = company_cols[0]
            company_counts = data[main_company_col].value_counts()
            insights['companies'] = {
                'total_companies': len(company_counts),
                'top_companies': company_counts.head(10).to_dict()
            }
        
        # Clinical trials analysis
        if trial_cols:
            trial_status_cols = [col for col in trial_cols if 'status' in col.lower()]
            if trial_status_cols:
                status_counts = data[trial_status_cols[0]].value_counts()
                insights['clinical_trials'] = {
                    'trial_statuses': status_counts.to_dict()
                }
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating pharmaceutical insights: {str(e)}'}), 500

@app.route('/api/export_options')
def export_options():
    """Get available export options for the current analysis."""
    try:
        options = {
            'available_formats': ['SQL', 'Excel', 'PNG', 'SVG', 'PDF'],
            'available_normalizations': [],
            'files_generated': {}
        }
        
        # Check what normalizations are available
        if 'relations_3nf' in analysis_results:
            options['available_normalizations'].append('3nf')
            
        if 'relations_bcnf' in analysis_results:
            options['available_normalizations'].append('bcnf')
        
        # List generated files
        export_dir = 'exports'
        if os.path.exists(export_dir):
            for filename in os.listdir(export_dir):
                filepath = os.path.join(export_dir, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    options['files_generated'][filename] = {
                        'size_bytes': file_size,
                        'size_mb': file_size / 1024 / 1024,
                        'modified': os.path.getmtime(filepath)
                    }
        
        return jsonify({
            'success': True,
            'export_options': options
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting export options: {str(e)}'}), 500

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