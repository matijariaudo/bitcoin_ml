Project summary
This project aims to support Bitcoin savers by helping them make more informed decisions about when to sell and rebuy the same amount of Bitcoin after a price drop. The objective is to minimize losses and optimize asset accumulation through strategic timing.

Two modeling approaches were explored: Logistic Regression and XGBoost, as well as ensemble combinations of both. After careful evaluation, XGBoost emerged as the most effective model, offering superior performance in capturing relevant market patterns.

To enhance the reliability of predictions, a custom decision threshold of 70% was introduced to define a "drop" scenario. This deliberate choice reduces false positives, thereby improving precision—an essential factor given the nature of the decision: if the model signals a drop, the user is expected to sell. While this adjustment comes at the cost of recall (some actual drops may not be predicted), it aligns with the project's core priority: trustworthy alerts when action is needed.

In essence, the model favors high-confidence signals over quantity, ensuring that when it predicts a fall, it's more likely to be right—protecting the user from unnecessary trades and fostering more efficient re-entry into the market.

See demo: http://18.230.227.217:8000/

Model scores
| Class       | Precision | Recall  | F1-Score | Support |
|-------------|-----------|---------|----------|---------|
| No sign     | 0.6893    | 0.9748  | 0.8075   | 2064    |
| Price drop  | 0.8360    | 0.2261  | 0.3559   | 1172    |
