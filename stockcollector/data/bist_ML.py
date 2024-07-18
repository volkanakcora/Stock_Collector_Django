import datetime
import pandas as pd
from django.conf import settings
from .models import StockBST
import logging
from django.apps import AppConfig 
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import RandomizedSearchCV
from .utils import functions

class StocksBSTPredict(AppConfig):
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
        historical_data = StockBST.objects.all()
        historical_df = pd.DataFrame(list(historical_data.values()))

        features = ['open_price', 'high_price', 'low_price', 'close_price', 'volume',
                    'daily_return', 'volatility', 'daily_change', 'high_low_spread', 'expected_change']

        historical_df['y_true'] = (historical_df['close_price'].shift(-30) > historical_df['close_price'] * 1.40).astype(int)

        X = historical_df[features]
        y = historical_df['y_true']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(random_state=42))
        ])

        param_dist = {
            'classifier__n_estimators': [50],
            'classifier__max_depth': [None],
            'classifier__min_samples_split': [2],
            'classifier__min_samples_leaf': [1]
        }

        randomized_search = RandomizedSearchCV(pipeline, param_distributions=param_dist, n_iter=20, cv=5, scoring='f1', n_jobs=-1, random_state=42)

        randomized_search.fit(X_train, y_train)

        self.model = randomized_search.best_estimator_
        y_pred = self.model.predict(X_test)


        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        logging.info(f"Best Parameters: {randomized_search.best_params_}")
        logging.info(f"Model Accuracy: {accuracy}")
        logging.info(f"Model Precision: {precision}")
        logging.info(f"Model Recall: {recall}")
        logging.info(f"Model F1 Score: {f1}")
        logging.info(f"Interpretation {randomized_search.best_score_}")
        print("Model training completed.")

    def detect_pattern(self):
        data = StockBST.objects.filter(date__gte=datetime.date.today() - datetime.timedelta(days=35))
        data_df = pd.DataFrame(list(data.values()))

        if data_df.empty:
            logging.info("No new data available for pattern detection.")
            return

        data_df.reset_index(drop=True, inplace=True)
        unique_stocks = data_df['stock_name'].unique()
        stocks_likely_to_increase = []

        for stock in unique_stocks:
            stock_data = data_df[data_df['stock_name'] == stock]
            if len(stock_data) < 20:
                continue

            stock_features = stock_data[[
                'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                'daily_return', 'volatility', 'daily_change', 'high_low_spread', 'expected_change'
            ]]

            predictions = self.model.predict(stock_features)

            if hasattr(self.model, 'predict_proba'):
                predicted_probabilities = self.model.predict_proba(stock_features)[:, 1]
            else:
                predicted_probabilities = None

            if predictions.sum() > 0 and predicted_probabilities is not None:
                stocks_likely_to_increase.append({
                    'stock_name': stock,
                    'predicted_probabilities': predicted_probabilities.mean()  
                })

        filtered_stocks = [stock for stock in stocks_likely_to_increase if stock['predicted_probabilities'] is not None]
        filtered_stocks.sort(key=lambda x: x['predicted_probabilities'], reverse=True)

        top_candidates = [stock['stock_name'] for stock in filtered_stocks[:10]]

        if top_candidates:
            logging.info(f"Top stocks likely to increase by more than 40%: {top_candidates}")
            functions.send_message(f" BIST TURKEY Top stocks likely to increase by more than 40%: {top_candidates}")
        else:
            logging.info("No stocks are likely to increase by more than 40% in the last month.")

        logging.info("Pattern detection completed.")
