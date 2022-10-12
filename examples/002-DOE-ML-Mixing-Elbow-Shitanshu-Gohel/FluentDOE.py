"""
002-DOE-ML-Mixing-Elbow
===================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# Import modules
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import matplotlib.pyplot as plt  # noqa: F401
import numpy as np
import pandas as pd  # noqa: F401

# import plotly.graph_objects as go  # noqa: F401
import seaborn as sns  # noqa: F401

import_filename = examples.download_file(
    "elbow.cas.h5", "pyfluent/examples/002-DOE-ML-Mixing-Elbow-Shitanshu-Gohel"
)  # noqa: E501

# Create a session object
session = pyfluent.launch_fluent(mode="solver")

# Check server status
session.check_health()

# Read a case file
session.tui.file.read_case(import_filename)

# Define Manual DOE as numpy arrays
coldVelArr = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
hotVelArr = np.array([0.8, 1, 1.2, 1.4, 1.6, 1.8, 2.0])
resArr = np.zeros((coldVelArr.shape[0], hotVelArr.shape[0]))

# Run cases in sequence
# Populate results (Mass Weighted Average of Temperature at Outlet) in resArr
for idx1, coldVel in np.ndenumerate(coldVelArr):
    for idx2, hotVel in np.ndenumerate(hotVelArr):

        inlet1 = session.setup.boundary_conditions.velocity_inlet["cold-inlet"]
        inlet1.vmag.value = coldVel

        inlet2 = session.setup.boundary_conditions.velocity_inlet["hot-inlet"]
        inlet2.vmag.value = hotVel

        session.solution.initialization()
        session.tui.solve.iterate(5)  # 200

        session.solution.report_definitions.surface["outlet-temp-avg"] = {}

        session.solution.report_definitions.surface[
            "outlet-temp-avg"
        ].report_type = "surface-massavg"

        session.solution.report_definitions.surface[
            "outlet-temp-avg"
        ].field = "temperature"

        session.solution.report_definitions.surface["outlet-temp-avg"].surface_names = [
            "outlet"
        ]

        output = session.solution.report_definitions.compute(
            report_defs=["outlet-temp-avg"]
        )

        resArr[idx1][idx2] = output[0]["outlet-temp-avg"][0]

# End current session
# session.exit()

# # Define Manual DOE as numpy arrays
# coldVelArr = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
# hotVelArr = np.array([0.8, 1, 1.2, 1.4, 1.6, 1.8, 2.0])
# resArr = np.array(
#     [
#         [299.68665, 300.69921, 301.56705, 302.34852, 302.98525, 303.58664, 304.06953],
#         [297.05361, 297.80859, 298.4808, 299.10745, 299.6902, 300.22034, 300.70074],
#         [295.9343, 296.51279, 297.0535, 297.56171, 298.04696, 298.47616, 298.90577],
#         [295.31416, 295.7837, 296.22907, 296.65212, 297.05474, 297.43761, 297.80631],
#         [294.91981, 295.31458, 295.6923, 296.05425, 296.40156, 296.73504, 297.05574],
#         [294.64707, 294.9871, 295.31467, 295.63081, 295.9354, 296.23001, 296.51455],
#         [294.44734, 294.74565, 295.03459, 295.31482, 295.58626, 295.84967, 296.10494],
#     ]
# )
#
# # Define figure object
# fig = go.Figure(data=[go.Surface(z=resArr.T, x=coldVelArr, y=hotVelArr)])
#
# # Update figure layout
# fig.update_layout(
#     title={
#         "text": "Mixing Elbow Response Surface",
#         "y": 0.9,
#         "x": 0.5,
#         "xanchor": "center",
#         "yanchor": "top",
#     }
# )
#
# fig.update_layout(
#     scene=dict(
#         xaxis_title="Cold Inlet Vel (m/s)",
#         yaxis_title="Hot Inlet Vel (m/s)",
#         zaxis_title="Average Outlet Temperature (K)",
#     ),
#     width=600,
#     height=600,
#     margin=dict(l=80, r=80, b=80, t=80),
# )
# # Show figure
# fig.show()
#
# # Create a dataframe
# df = pd.DataFrame(columns=["coldVel", "hotVel", "Result"])
#
# # Add temperatures to dataframe
# for idx1, coldVel in np.ndenumerate(coldVelArr):
#     for idx2, hotVel in np.ndenumerate(hotVelArr):
#         tempDict = {"coldVel": coldVel, "hotVel": hotVel, "Result": resArr[idx1][idx2]}  # noqa: E501
#         df = df.append(tempDict, ignore_index=True)
#
# from sklearn.compose import ColumnTransformer
#
# # Import modules
# from sklearn.model_selection import train_test_split
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import PolynomialFeatures, StandardScaler
#
# # Define polynomial features
# poly_features = PolynomialFeatures(degree=1, include_bias=False)
#
# # Define pipeline
# transformer1 = Pipeline(
#     [
#         ("poly_features", poly_features),
#         ("std_scaler", StandardScaler()),
#     ]
# )
#
# # Apply column wise transformations
# x_ct = ColumnTransformer(
#     [
#         ("transformer1", transformer1, ["coldVel", "hotVel"]),
#     ],
#     remainder="drop",
# )
#
# # Train-test split
# train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)
#
# # Transform train and test dataset
# X_train = x_ct.fit_transform(train_set)
# X_test = x_ct.fit_transform(test_set)
#
# y_train = train_set["Result"]
# y_test = test_set["Result"]
# y_train = np.ravel(y_train.T)
# y_test = np.ravel(y_test.T)
#
# # from pprint import pprint
# from sklearn.metrics import r2_score
#
# # Import requirements
# # from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import RepeatedKFold, cross_val_score
#
# # from sklearn.ensemble import RandomForestRegressor
# from xgboost import XGBRegressor
#
# # Set precision level
# np.set_printoptions(precision=2)
#
# # Function to display scores
# def display_scores(scores):
#     print("\nCross-Validation Scores:", scores)
#     print("Mean:%0.2f" % (scores.mean()))
#     print("Std. Dev.:%0.2f" % (scores.std()))
#
#
# # Function to fit the model and predict on test data set
# def fit_and_predict(model):
#     cv = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)
#     cv_scores = cross_val_score(
#         model, X_train, y_train, scoring="neg_mean_squared_error", cv=cv
#     )
#     rmse_scores = np.sqrt(-cv_scores)
#     display_scores(rmse_scores)
#
#     model.fit(X_train, y_train)
#     train_predictions = model.predict(X_train)
#     test_predictions = model.predict(X_test)
#     print("\n\nCoefficient Of Determination")
#     print("Train Data R2 Score: %0.3f" % (r2_score(train_predictions, y_train)))
#     print("Test Data R2 Score: %0.3f" % (r2_score(test_predictions, y_test)))
#     print(
#         "\n\nPredictions - Ground Truth (Kelvin): ", (test_predictions - y_test), "\n"
#     )
#     #    print("\n\nModel Parameters:")
#     #    pprint(model.get_params())
#
#     fig = plt.figure(figsize=(12, 5))
#
#     fig.add_subplot(121)
#     sns.regplot(x=y_train, y=train_predictions, color="g")
#     plt.title("Train Data", fontsize=16)
#     plt.xlabel("Ground Truth", fontsize=12)
#     plt.ylabel("Predictions", fontsize=12)
#
#     fig.add_subplot(122)
#     sns.regplot(x=y_test, y=test_predictions, color="g")
#     plt.title("Test/Unseen Data", fontsize=16)
#     plt.xlabel("Ground Truth", fontsize=12)
#     plt.ylabel("Predictions", fontsize=12)
#
#     plt.tight_layout()
#     plt.show()
#
#
# # Define model object
# # model = LinearRegression()
# model = XGBRegressor(
#     n_estimators=100, max_depth=10, eta=0.3, subsample=0.8, random_state=42
# )
# # model = RandomForestRegressor(random_state=42)
#
# # Fit the model and predict on test data set
# fit_and_predict(model)
#
# # Import modules
# import tensorflow as tf
# from tensorflow import keras
#
# print("TensorFlow version is:", tf.__version__)
# keras.backend.clear_session()
# np.random.seed(42)
# tf.random.set_seed(42)
#
# # Define Sequential model
# model = keras.models.Sequential(
#     [
#         keras.layers.Dense(
#             10,
#             activation="relu",
#             input_shape=X_train.shape[1:],
#             kernel_initializer="lecun_normal",
#         ),
#         keras.layers.BatchNormalization(),
#         keras.layers.Dense(10, activation="relu", kernel_initializer="lecun_normal"),
#         keras.layers.BatchNormalization(),
#         keras.layers.Dense(1),
#     ]
# )
#
# # Optimize the model
# optimizer = tf.keras.optimizers.Adam(lr=0.1, beta_1=0.9, beta_2=0.999)
#
# # Compile the model
# model.compile(loss="mean_squared_error", optimizer=optimizer)
# checkpoint_cb = keras.callbacks.ModelCheckpoint(
#     "my_keras_model.h5", save_best_only=True
# )
# early_stopping_cb = keras.callbacks.EarlyStopping(
#     patience=30, restore_best_weights=True
# )
#
# # Print model summary
# model.summary()
#
# # keras.utils.plot_model(model, show_shapes=True,) # to_file='dot_img.png', )
#
# # Train model
# history = model.fit(
#     X_train,
#     y_train,
#     epochs=250,
#     validation_split=0.2,
#     callbacks=[checkpoint_cb, early_stopping_cb],
# )
# model = keras.models.load_model("my_keras_model.h5")
#
# # Print training parameters
# print(history.params)
#
# # Plot figures based on model history
# pd.DataFrame(history.history).plot(figsize=(8, 5))
# plt.grid(True)
# plt.show()
#
# # Define train test predictions
# train_predictions = model.predict(X_train)
# test_predictions = model.predict(X_test)
# train_predictions = np.ravel(train_predictions.T)
# test_predictions = np.ravel(test_predictions.T)
#
# # Print Accuracy
# print("\n\nTrain R2: %0.3f" % (r2_score(train_predictions, y_train)))
# print("Test R2: %0.3f" % (r2_score(test_predictions, y_test)))
# print("Predictions - Ground Truth (Kelvin): ", (test_predictions - y_test))
#
# # Plot figures
# fig = plt.figure(figsize=(12, 5))
#
# fig.add_subplot(121)
# sns.regplot(x=y_train, y=train_predictions, color="g")
# plt.title("Train", fontsize=16)
# plt.xlabel("Ground Truth", fontsize=12)
# plt.ylabel("Predictions", fontsize=12)
#
# fig.add_subplot(122)
# sns.regplot(x=y_test, y=test_predictions, color="g")
# plt.title("Test", fontsize=16)
# plt.xlabel("Ground Truth", fontsize=12)
# plt.ylabel("Predictions", fontsize=12)
#
# plt.tight_layout()
# plt.show()
