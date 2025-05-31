# Dublin Rent Predictor - Jupyter Notebook

This repository contains a comprehensive Jupyter notebook that demonstrates the complete machine learning pipeline for predicting rental prices in Dublin, Ireland.

## 📓 Notebook Overview

The `dublin_rent_predictor_notebook.ipynb` file provides a step-by-step walkthrough of:

1. **Data Loading & Exploration** - Loading and examining the Dublin rental dataset
2. **Data Cleaning & Preprocessing** - Handling missing values, extracting Dublin postal codes
3. **Data Visualization & Analysis** - Creating insightful charts and statistics
4. **Feature Engineering** - One-hot encoding categorical variables
5. **Model Training** - Training a Random Forest Regressor
6. **Model Evaluation** - Comprehensive performance metrics and visualizations
7. **Feature Importance Analysis** - Understanding which factors drive rent prices
8. **Making Predictions** - Testing the model with example properties
9. **Model Persistence** - Saving the trained model for future use

## 🚀 Getting Started

### Prerequisites

Make sure you have the following Python packages installed:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
```

Or if you're using the project's backend environment:

```bash
cd src/backend
pip install -r requirements.txt  # or use uv/poetry as configured
pip install jupyter matplotlib seaborn
```

### Running the Notebook

1. **Start Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```

2. **Open the notebook:**
   Navigate to `dublin_rent_predictor_notebook.ipynb` in the Jupyter interface

3. **Run all cells:**
   - Use `Cell > Run All` to execute the entire notebook
   - Or run cells individually with `Shift + Enter`

## 📊 What You'll Learn

### Data Insights
- **Dataset**: 776 Dublin rental listings from Daft.ie
- **Coverage**: 21 Dublin postal areas, 3 property types
- **Price Range**: €500 - €20,000 per month
- **Average Rent**: ~€2,809 per month

### Model Performance
- **Algorithm**: Random Forest Regressor (100 trees)
- **R² Score**: ~47% (explains 47% of price variance)
- **Mean Absolute Error**: ~€469
- **Training/Test Split**: 620/156 samples

### Key Findings
- **Most Important Features**:
  1. Bathrooms (53.5% importance)
  2. Bedrooms (24.7% importance)
  3. Dublin 4 location (11.5% importance)

- **Most Expensive Areas**: Dublin 4, Dublin 2, Dublin 1
- **Property Types**: Apartments (64.4%), Houses (26.0%), Studios (9.5%)

## 📈 Visualizations Included

The notebook generates several informative plots:

- **Price Distribution**: Histogram showing rent price spread
- **Property Type Breakdown**: Pie chart of property types
- **Area Analysis**: Bar charts of average prices by Dublin area
- **Model Performance**: Predicted vs actual prices scatter plot
- **Feature Importance**: Horizontal bar chart of top features
- **Residuals Analysis**: Distribution of prediction errors

## 🔧 Technical Details

### Data Processing Pipeline
1. **Address Parsing**: Extracts Dublin postal codes using regex patterns
2. **Data Cleaning**: Removes invalid prices and missing values
3. **Feature Engineering**: One-hot encoding for categorical variables
4. **Model Training**: Random Forest with optimized hyperparameters

### Model Architecture
```python
RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)
```

### Feature Set
- **Numeric**: Bedrooms, Bathrooms
- **Categorical**: Property Type (Apartment/House/Studio)
- **Location**: Dublin Area (1-24 postal codes)

## 💾 Output Files

The notebook saves several artifacts to `notebook_models/`:

- `dublin_rent_model.joblib` - Trained model + encoders
- `model_metrics.json` - Performance metrics
- `feature_importance.json` - Feature importance scores

## 🔗 Integration with Web App

This notebook demonstrates the same ML pipeline used in the production web application:

- **Backend**: FastAPI server (`src/backend/main.py`)
- **Frontend**: Next.js React app (`src/frontend/`)
- **Model Classes**: `RentalPricePredictor` and `DataProcessor`

## 📝 Example Predictions

The notebook includes example predictions for:

- 2-bed apartment in Dublin 4: €3,996/month
- 1-bed apartment in Dublin 1: €2,600/month  
- 3-bed house in Dublin 6: €4,200/month
- Studio in Dublin 8: €1,850/month
- 4-bed house in Dublin 2: €5,500/month

## 🎯 Next Steps

After running the notebook, you can:

1. **Experiment with different algorithms** (XGBoost, Neural Networks)
2. **Add more features** (property size, amenities, transport links)
3. **Collect more training data** for improved accuracy
4. **Deploy the model** using the FastAPI backend
5. **Create real-time predictions** through the web interface

## 🤝 Contributing

Feel free to:
- Add new visualizations
- Experiment with different models
- Improve data preprocessing
- Add feature engineering techniques

## 📄 License

This notebook is part of the Dublin Rent Predictor project and follows the same licensing terms.
