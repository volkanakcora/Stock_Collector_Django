import datetime
import pandas as pd
from django.conf import settings
from .models import Stock
import logging
from django.apps import AppConfig 
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import RandomizedSearchCV
from .utils import functions

class StocksPredict(AppConfig):
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)
        self.model = None

    def run(self):
        try:
            self.train_model()
            self.detect_pattern()
        except Exception as e:
            logging.warning(f"Process failed: {str(e)}")

    def train_model(self):
        # Define feature list
        features = ['open_price', 'high_price', 'low_price', 'close_price', 'volume',
                    'daily_return', 'volatility', 'daily_change', 'high_low_spread', 'expected_change']

        # Fetch historical data from the database using queryset iterator
        historical_data = Stock.objects.all().iterator()

        # Initialize lists for training data
        X_train = []
        y_train = []

        # Iterate over the queryset in chunks
        for chunk in historical_data:
            # Perform feature engineering and append to training data
            y_true = 1 if (chunk.close_price * 1.40 < self.get_future_close_price(chunk)) else 0
            X_train.append([getattr(chunk, feature) for feature in features])
            y_train.append(y_true)

            # Process training data in batches (adjust batch size as needed)
            if len(X_train) >= 100000:
                self.process_training_batch(X_train, y_train)
                X_train = []
                y_train = []

        # Final batch processing
        if X_train:
            self.process_training_batch(X_train, y_train)

        logging.info("Model training completed.")

    def get_future_close_price(self, stock_obj):
        future_stock = Stock.objects.filter(pk=stock_obj.pk + 30).first()  # Adjust as per your logic
        if future_stock:
            return future_stock.close_price
        return 0  # Handle cases where future data may not be available

    def process_training_batch(self, X_train, y_train):
        # Split the batch into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

        # Define a pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(random_state=42))
        ])

        # Define the parameter distribution
        param_dist = {
            'classifier__n_estimators': [50],
            'classifier__max_depth': [None],
            'classifier__min_samples_split': [2],
            'classifier__min_samples_leaf': [1]
        }

        # Perform randomized search with cross-validation
        randomized_search = RandomizedSearchCV(pipeline, param_distributions=param_dist, n_iter=20, cv=5, scoring='f1', n_jobs=-1, random_state=42)
        randomized_search.fit(X_train, y_train)

        # Get the best model
        self.model = randomized_search.best_estimator_

        # Make predictions on the test set
        y_pred = self.model.predict(X_test)

        # Calculate and log performance metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        logging.info(f"Best Parameters: {randomized_search.best_params_}")
        logging.info(f"Model Accuracy: {accuracy}")
        logging.info(f"Model Precision: {precision}")
        logging.info(f"Model Recall: {recall}")
        logging.info(f"Model F1 Score: {f1}")

    def detect_pattern(self):
        # Fetch data for the last month
        data = Stock.objects.filter(date__gte=datetime.date.today() - datetime.timedelta(days=35))
        data_df = pd.DataFrame(list(data.values()))

        if data_df.empty:
            logging.info("No new data available for pattern detection.")
            return

        # Process and calculate values
        data_df.reset_index(drop=True, inplace=True)

        # Get unique stock names
        unique_stocks = data_df['stock_name'].unique()

        # Initialize a list to hold the names of stocks likely to increase
        stocks_likely_to_increase = []

        for stock in unique_stocks:
            stock_data = data_df[data_df['stock_name'] == stock]

            # Ensure there is enough data for prediction
            if len(stock_data) < 20:
                continue

            # Feature engineering (adjust based on your feature set)
            stock_features = stock_data[[
                'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                'daily_return', 'volatility', 'daily_change', 'high_low_spread', 'expected_change'
            ]]

            # Predict using the trained model
            predictions = self.model.predict(stock_features)

            # Calculate probabilities if available
            if hasattr(self.model, 'predict_proba'):
                predicted_probabilities = self.model.predict_proba(stock_features)[:, 1]
            else:
                predicted_probabilities = None

            # Determine if any prediction indicates a 40% increase
            if predictions.sum() > 0 and predicted_probabilities is not None:
                stocks_likely_to_increase.append({
                    'stock_name': stock,
                    'predicted_probabilities': predicted_probabilities.mean()
                })

        # Filter stocks based on your thresholds and sort by predicted probability
        filtered_stocks = [stock for stock in stocks_likely_to_increase if stock['predicted_probabilities'] is not None]
        filtered_stocks.sort(key=lambda x: x['predicted_probabilities'], reverse=True)

        # Select top candidates for investment (e.g., top 10 stocks)
        top_candidates = [stock['stock_name'] for stock in filtered_stocks[:10]]

        if top_candidates:
            logging.info(f"Top stocks likely to increase by more than 40%: {top_candidates}")
            functions.send_message(f"Foreign Top stocks likely to increase by more than 40%: {top_candidates}")
            
        else:
            logging.info("No stocks are likely to increase by more than 40% in the last month.")

        logging.info("Pattern detection completed.")
