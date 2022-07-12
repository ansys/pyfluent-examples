#!/usr/bin/env python
# coding: utf-8

# # <span style='color:Blue'>_PyFluent with ML Python Packages_</span>
# ### <span style='color:Blue'>_Set Working Directory_</span>
# ### <span style='color:Blue'>_Launch Fluent_</span>
# ### <span style='color:Blue'>_Read Case_</span>

# In[1]:


import os

import ansys.fluent.core as pyfluent
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# In[2]:


workDir = "D:/Examples/002 DOE ML (Mixing Elbow) - Shitanshu Gohel"
caseName = "elbow.cas.h5"

caseFilePath = os.path.join(os.getcwd(), workDir, caseName)

os.chdir(os.path.join(os.getcwd(), workDir))


# In[3]:


session = pyfluent.launch_fluent(show_gui=True)


# In[4]:


session.check_health()


# In[5]:


session.solver.tui.file.read_case(case_file_name=caseFilePath)


# In[6]:


session.solver.root.setup.obj_name


# ### <span style='color:Blue'>_Define Manual DOE as numpy arrays_</span>
# ### <span style='color:Blue'>_Run cases in sequence_</span>
# ### <span style='color:Blue'>_Populate results (Mass Weighted Average of Temperature at Outlet) in resArr_</span>  # noqa: E501

# In[7]:


root = session.solver.root


# In[8]:


coldVelArr = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
hotVelArr = np.array([0.8, 1, 1.2, 1.4, 1.6, 1.8, 2.0])
resArr = np.zeros((coldVelArr.shape[0], hotVelArr.shape[0]))

for idx1, coldVel in np.ndenumerate(coldVelArr):
    for idx2, hotVel in np.ndenumerate(hotVelArr):

        inlet1 = root.setup.boundary_conditions.velocity_inlet["cold-inlet"]
        inlet1.vmag.constant = coldVel

        inlet2 = root.setup.boundary_conditions.velocity_inlet["hot-inlet"]
        inlet2.vmag.constant = hotVel

        session.solver.root.solution.initialization()
        session.solver.tui.solve.iterate(5)  # 200

        root.solution.report_definitions.surface["outlet-temp-avg"] = {}

        root.solution.report_definitions.surface[
            "outlet-temp-avg"
        ].report_type = "surface-massavg"

        root.solution.report_definitions.surface[
            "outlet-temp-avg"
        ].field = "temperature"

        root.solution.report_definitions.surface["outlet-temp-avg"].surface_names = [
            "outlet"
        ]

        output = root.solution.report_definitions.compute(
            report_defs=["outlet-temp-avg"]
        )

        resArr[idx1][idx2] = output["outlet-temp-avg"][0]


# In[9]:


resArr


# In[10]:


session.exit()


# In[11]:


coldVelArr = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
hotVelArr = np.array([0.8, 1, 1.2, 1.4, 1.6, 1.8, 2.0])
resArr = np.array(
    [
        [299.68665, 300.69921, 301.56705, 302.34852, 302.98525, 303.58664, 304.06953],
        [297.05361, 297.80859, 298.4808, 299.10745, 299.6902, 300.22034, 300.70074],
        [295.9343, 296.51279, 297.0535, 297.56171, 298.04696, 298.47616, 298.90577],
        [295.31416, 295.7837, 296.22907, 296.65212, 297.05474, 297.43761, 297.80631],
        [294.91981, 295.31458, 295.6923, 296.05425, 296.40156, 296.73504, 297.05574],
        [294.64707, 294.9871, 295.31467, 295.63081, 295.9354, 296.23001, 296.51455],
        [294.44734, 294.74565, 295.03459, 295.31482, 295.58626, 295.84967, 296.10494],
    ]
)


# ### <span style='color:Blue'>_Plot Response Surface using Plotly_</span>

# In[12]:


import plotly.graph_objects as go

fig = go.Figure(data=[go.Surface(z=resArr.T, x=coldVelArr, y=hotVelArr)])

fig.update_layout(
    title={
        "text": "Mixing Elbow Response Surface",
        "y": 0.9,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }
)

fig.update_layout(
    scene=dict(
        xaxis_title="Cold Inlet Vel (m/s)",
        yaxis_title="Hot Inlet Vel (m/s)",
        zaxis_title="Average Outlet Temperature (K)",
    ),
    width=600,
    height=600,
    margin=dict(l=80, r=80, b=80, t=80),
)
fig.show()


# # <span style='color:Blue'>_Supervised ML for a Regression Task_</span>

# ### <span style='color:Blue'>_Create Pandas Dataframe for ML Model Input_</span>

# In[54]:


import pandas as pd

df = pd.DataFrame(columns=["coldVel", "hotVel", "Result"])

for idx1, coldVel in np.ndenumerate(coldVelArr):
    for idx2, hotVel in np.ndenumerate(hotVelArr):
        tempDict = {"coldVel": coldVel, "hotVel": hotVel, "Result": resArr[idx1][idx2]}
        df = df.append(tempDict, ignore_index=True)


# ### <span style='color:Blue'>_Using scikit-learn_</span>
# ### <span style='color:Blue'>_Prepare Features (X) and Label (y) using a Pre-Processing Pipeline_</span>  # noqa: E501
# ### <span style='color:Blue'>_Train-Test (80-20) Split_</span>
# ### <span style='color:Blue'>_Add Polynomial Features to improve ML Model_</span>

# In[61]:


from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

poly_features = PolynomialFeatures(degree=1, include_bias=False)

transformer1 = Pipeline(
    [
        ("poly_features", poly_features),
        ("std_scaler", StandardScaler()),
    ]
)


x_ct = ColumnTransformer(
    [
        ("transformer1", transformer1, ["coldVel", "hotVel"]),
    ],
    remainder="drop",
)

train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)

X_train = x_ct.fit_transform(train_set)
X_test = x_ct.fit_transform(test_set)

y_train = train_set["Result"]
y_test = test_set["Result"]
y_train = np.ravel(y_train.T)
y_test = np.ravel(y_test.T)


# In[62]:


X_train.shape


# ## <span style='color:Blue'>_Define functions for:_</span>
# ### <span style='color:Blue'>_Cross-Validation and Display Scores (scikit-learn)_</span>  # noqa: E501
# ### <span style='color:Blue'>_Training the Model (scikit-learn)_</span>
# ### <span style='color:Blue'>_Prediction on Unseen/Test Data (scikit-learn)_</span>
# ### <span style='color:Blue'>_Parity Plot (Matplotlib and Seaborn)_</span>

# In[46]:


# from pprint import pprint

# from sklearn.ensemble import RandomForestRegressor
# from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import RepeatedKFold, cross_val_score
from xgboost import XGBRegressor

np.set_printoptions(precision=2)


def display_scores(scores):
    print("\nCross-Validation Scores:", scores)
    print("Mean:%0.2f" % (scores.mean()))
    print("Std. Dev.:%0.2f" % (scores.std()))


def fit_and_predict(model):
    cv = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)
    cv_scores = cross_val_score(
        model, X_train, y_train, scoring="neg_mean_squared_error", cv=cv
    )
    rmse_scores = np.sqrt(-cv_scores)
    display_scores(rmse_scores)

    model.fit(X_train, y_train)
    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)
    print("\n\nCoefficient Of Determination")
    print("Train Data R2 Score: %0.3f" % (r2_score(train_predictions, y_train)))
    print("Test Data R2 Score: %0.3f" % (r2_score(test_predictions, y_test)))
    print(
        "\n\nPredictions - Ground Truth (Kelvin): ", (test_predictions - y_test), "\n"
    )
    #    print("\n\nModel Parameters:")
    #    pprint(model.get_params())

    fig = plt.figure(figsize=(12, 5))

    fig.add_subplot(121)
    sns.regplot(x=y_train, y=train_predictions, color="g")
    plt.title("Train Data", fontsize=16)
    plt.xlabel("Ground Truth", fontsize=12)
    plt.ylabel("Predictions", fontsize=12)

    fig.add_subplot(122)
    sns.regplot(x=y_test, y=test_predictions, color="g")
    plt.title("Test/Unseen Data", fontsize=16)
    plt.xlabel("Ground Truth", fontsize=12)
    plt.ylabel("Predictions", fontsize=12)

    plt.tight_layout()
    plt.show()


# ### <span style='color:Blue'>_Select the Model from Linear, Random Forest or XGBoost_</span>  # noqa: E501
# ### <span style='color:Blue'>_Call fit_and_predict_</span>

# In[63]:


# model = LinearRegression()
model = XGBRegressor(
    n_estimators=100, max_depth=10, eta=0.3, subsample=0.8, random_state=42
)
# model = RandomForestRegressor(random_state=42)

fit_and_predict(model)


# ### <span style='color:Blue'>_TensorFlow and Keras Neural Network Regression_</span>

# In[31]:


import tensorflow as tf
from tensorflow import keras

print("TensorFlow version is:", tf.__version__)
keras.backend.clear_session()
np.random.seed(42)
tf.random.set_seed(42)

model = keras.models.Sequential(
    [
        keras.layers.Dense(
            10,
            activation="relu",
            input_shape=X_train.shape[1:],
            kernel_initializer="lecun_normal",
        ),
        keras.layers.BatchNormalization(),
        keras.layers.Dense(10, activation="relu", kernel_initializer="lecun_normal"),
        keras.layers.BatchNormalization(),
        keras.layers.Dense(1),
    ]
)

optimizer = tf.keras.optimizers.Adam(lr=0.1, beta_1=0.9, beta_2=0.999)

model.compile(loss="mean_squared_error", optimizer=optimizer)
checkpoint_cb = keras.callbacks.ModelCheckpoint(
    "my_keras_model.h5", save_best_only=True
)
early_stopping_cb = keras.callbacks.EarlyStopping(
    patience=30, restore_best_weights=True
)

model.summary()

# keras.utils.plot_model(model, show_shapes=True,) # to_file='dot_img.png', )

history = model.fit(
    X_train,
    y_train,
    epochs=250,
    validation_split=0.2,
    callbacks=[checkpoint_cb, early_stopping_cb],
)
model = keras.models.load_model("my_keras_model.h5")


print(history.params)

pd.DataFrame(history.history).plot(figsize=(8, 5))
plt.grid(True)
plt.show()

train_predictions = model.predict(X_train)
test_predictions = model.predict(X_test)
train_predictions = np.ravel(train_predictions.T)
test_predictions = np.ravel(test_predictions.T)

print("\n\nTrain R2: %0.3f" % (r2_score(train_predictions, y_train)))
print("Test R2: %0.3f" % (r2_score(test_predictions, y_test)))
print("Predictions - Ground Truth (Kelvin): ", (test_predictions - y_test))

fig = plt.figure(figsize=(12, 5))

fig.add_subplot(121)
sns.regplot(x=y_train, y=train_predictions, color="g")
plt.title("Train", fontsize=16)
plt.xlabel("Ground Truth", fontsize=12)
plt.ylabel("Predictions", fontsize=12)

fig.add_subplot(122)
sns.regplot(x=y_test, y=test_predictions, color="g")
plt.title("Test", fontsize=16)
plt.xlabel("Ground Truth", fontsize=12)
plt.ylabel("Predictions", fontsize=12)

plt.tight_layout()
plt.show()


# In[ ]:
