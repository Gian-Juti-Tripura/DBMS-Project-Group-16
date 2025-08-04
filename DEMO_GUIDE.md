# PharmaCare Analytics Dashboard - Demo Guide

## 🚀 Quick Start Demo

### Step 1: Start the Application
```bash
python3 run_simple.py
```

### Step 2: Open Your Browser
Navigate to: `http://localhost:5000`

### Step 3: Load Sample Data
1. Click the green **"Load Sample Data"** button
2. The system will load pharmaceutical data including:
   - 5 different drugs (cetuximab, etanercept, urokinase, abciximab, hydrocortisone)
   - Side effects, drug interactions, and disease information
   - Clinical trial data

### Step 4: Explore the Dashboard

#### 📊 Overview Cards
- **Total Records**: Shows number of pharmaceutical entries
- **Drug Categories**: Number of different drug types
- **Companies**: Number of pharmaceutical companies
- **Clinical Trials**: Number of trials with data

#### 🔍 Search & Filter
- **Search Box**: Try searching for:
  - `"cetuximab"` - find specific drug
  - `"cancer"` - find cancer-related entries
  - `"completed"` - find completed trials
- **Category Filter**: Filter by Drugs, Diseases, or Companies
- **Clear Filters**: Reset to show all data

#### 📈 Analytics Charts
- **Drug Categories**: Pie chart showing distribution
- **Top Companies**: Bar chart of pharmaceutical companies
- **Disease Categories**: Doughnut chart of disease types
- **Side Effects**: Most common side effects
- **Clinical Trials**: Trial status and participants

## 🔧 Upload Your Own Data

### CSV Format Requirements
Your CSV file should have these columns:
```
drug_name, side_effect_1, side_effect_2, ..., disease_name, disease_category, 
drug_category, product_name, company_name, clinical_trial_title, 
clinical_trial_participants, clinical_trial_status, ...
```

### Sample Data Structure
```csv
drug name,side effect,side effect,disease name,disease category,drug category
cetuximab,somnolence,headache,Adenocarcinoma,Cancer,Antineoplastic agents
etanercept,dizziness,nausea,Asthma,Respiratory,Antirheumatic agents
```

### Upload Process
1. Click **"Choose File"** or drag & drop your CSV
2. Click **"Upload File"**
3. Wait for processing confirmation
4. Explore your data with the dashboard features

## 🎯 Key Features Demo

### 1. Data Browsing
- View paginated table of all pharmaceutical records
- See detailed drug information, side effects, and trial data
- Navigate through pages of data

### 2. Advanced Search
- Search across all fields simultaneously
- Category-specific filtering
- Real-time search results

### 3. Visual Analytics
- Interactive charts powered by Plotly.js
- Responsive design for all devices
- Professional pharmaceutical color schemes

### 4. Data Insights
- Identify most common side effects
- Compare pharmaceutical companies
- Analyze clinical trial outcomes
- Explore drug-disease relationships

## 📱 Mobile Friendly

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🔄 Real-time Updates

All charts and statistics update automatically when:
- New data is uploaded
- Search filters are applied
- Different datasets are loaded

## 💡 Tips for Best Experience

1. **Start with Sample Data**: Get familiar with features using built-in data
2. **Use Search Wisely**: Try different search terms to find patterns
3. **Explore Charts**: Hover over chart elements for detailed information
4. **Clear Filters**: Reset view to see full dataset after searching
5. **Mobile View**: Try the dashboard on your phone for on-the-go access

## 🔧 Troubleshooting

### Common Issues:
- **No charts showing**: Make sure you've loaded data first
- **Search not working**: Clear filters and try again
- **File upload fails**: Ensure CSV format is correct
- **Slow performance**: Large files may take time to process

### Solutions:
1. Refresh the browser page
2. Check file format matches requirements
3. Try with sample data first
4. Use CSV files under 16MB

## 🚀 Next Steps

After exploring the demo:
1. Upload your own pharmaceutical datasets
2. Customize search strategies for your data
3. Export insights from analytics charts
4. Share dashboard with your team

---

**Happy analyzing!** 🔬📊