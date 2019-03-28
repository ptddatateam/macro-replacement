import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
kfold=KFold(n_splits=5, random_state=0)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import ElasticNet
'''regressors'''


def lasso(X, y, params):
    X_train, X_test, y_train, y_test=train_test_split(X, y, random_state=0, train_size=.8)
    parameters={"alpha":params}
    las=Lasso(max_iter=1000000)
    model=GridSearchCV(las, parameters, cv=kfold, scoring="neg_mean_squared_error")
    model.fit(X_train, y_train)
    bestalpha=model.best_params_["alpha"]
    bestalpha=float(bestalpha)
    print("Best alpha: {}".format(bestalpha))
    l=Lasso(alpha=bestalpha, max_iter=100000, tol=0.001).fit(X_train, y_train)
    print("Number of features used: {}".format(np.sum(l.coef_!=0)))
    y_predtrain=l.predict(X_train)
    print("Root Mean Squared Error on train data: {}".format(sqrt(mean_squared_error(y_train, y_predtrain))))
    y_pred=l.predict(X_test)
    print("Root Mean Squared Error on test data: {}".format(sqrt(mean_squared_error(y_test, y_pred))))
    return l.coef_

def elasticnet(X, y, params):
    X_train, X_test, y_train, y_test=train_test_split(X, y, random_state=0, train_size=.7)
    parameters={"alpha":params}
    las=ElasticNet()
    model=GridSearchCV(las, parameters, cv=kfold, scoring="neg_mean_squared_error")
    model.fit(X_train, y_train)
    bestalpha=model.best_params_["alpha"]
    bestalpha=float(bestalpha)
    en=ElasticNet(alpha=bestalpha, max_iter=100000, tol=0.1).fit(X_train, y_train)
    print("Number of features used: {}".format(np.sum(en.coef_!=0)))
    y_predtrain=en.predict(X_train)
    print("Root Mean Squared Error on train data: {}".format(sqrt(mean_squared_error(y_train, y_predtrain))))
    y_pred=en.predict(X_test)
    print("Root Mean Squared Error on test data: {}".format(sqrt(mean_squared_error(y_test, y_pred))))
    return en.coef_


def ridge(X, y, params):
    X_train, X_test, y_train, y_test=train_test_split(X, y, random_state=0, train_size=.7)
    parameters={"alpha":params}
    las=Ridge()
    model=GridSearchCV(las, parameters, cv=kfold, scoring="neg_mean_squared_error")
    model.fit(X_train, y_train)
    bestalpha=model.best_params_["alpha"]
    bestalpha=float(bestalpha)
    ridge=Ridge(alpha=bestalpha, max_iter=100000, tol=0.1).fit(X_train, y_train)
    print("Number of features used: {}".format(np.sum(ridge.coef_!=0)))
    y_predtrain=ridge.predict(X_train)
    print("Root Mean Squared Error on train data: {}".format(sqrt(mean_squared_error(y_train, y_predtrain))))
    y_pred=ridge.predict(X_test)
    print("Root Mean Squared Error on test data: {}".format(sqrt(mean_squared_error(y_test, y_pred))))
    return ridge.coef_


def svr(X, y, C):
    X_train, X_test, y_train, y_test=train_test_split(X, y, random_state=0, train_size=.8)
    parameters={"C":C}
    svr=SVR()
    model=GridSearchCV(svr, parameters, cv=kfold, scoring="neg_mean_squared_error")
    model.fit(X_train, y_train)
    bestC=model.best_params_["C"]
    svr=SVR(C=bestC).fit(X_train, y_train)
    y_predtrain = svr.predict(X_train)
    print("Root Mean Squared Error on train data: {}".format(sqrt(mean_squared_error(y_train, y_predtrain))))
    y_pred=svr.predict(X_test)
    print("Root Mean Squared Error on test data: {}".format(sqrt(mean_squared_error(y_test, y_pred))))
    print("The parameters are: {}".format(bestC))
    return sqrt(mean_squared_error(y_train, y_predtrain)), sqrt(mean_squared_error(y_test, y_pred))


def rfr(X, y, mdparams, mlnparams, mslparams):
    X_train, X_test, y_train, y_test=train_test_split(X, y, random_state=0, train_size=.75)
    parameters={"max_depth":mdparams, "max_leaf_nodes":mlnparams, "min_samples_leaf": mslparams}
    rf=RandomForestRegressor(n_estimators=50)
    model=GridSearchCV(rf, parameters, cv=kfold, scoring="neg_mean_squared_error", n_jobs=3)
    model.fit(X_train, y_train)
    bestmd=model.best_params_["max_depth"]
    bestmln=model.best_params_["max_leaf_nodes"]
    bestmsl=model.best_params_["min_samples_leaf"]
    r=RandomForestRegressor(n_estimators=200,max_depth=bestmd, max_leaf_nodes=bestmln, min_samples_leaf=bestmsl).fit(X_train, y_train)
    y_predtrain=r.predict(X_train)
    print("Root Mean Squared Error on train data: {}".format(sqrt(mean_squared_error(y_train, y_predtrain))))
    y_pred=r.predict(X_test)
    print("Root Mean Squared Error on test data: {}".format(sqrt(mean_squared_error(y_test, y_pred))))
    print("The parameters are: {}".format([bestmd, bestmln, bestmsl]))
    return r.feature_importances_

def gbr(X, y, max_depth):
    X_train, X_test, y_train, y_test=train_test_split(X, y, random_state=0, train_size=.7)
    parameters={"max_depth":max_depth}
    gb=GradientBoostingRegressor(n_estimators=50, learning_rate=0.1, random_state=0, loss='ls')
    model=GridSearchCV(gb, parameters, cv=kfold, scoring="neg_mean_squared_error", n_jobs=3)
    model.fit(X_train, y_train)
    bestmd=model.best_params_["max_depth"]
    gb=GradientBoostingRegressor(n_estimators=200,max_depth=bestmd, learning_rate=0.1, random_state=0, loss='ls').fit(X_train, y_train)
    y_predtrain=gb.predict(X_train)
    print("Root Mean Squared Error on train data: {}".format(sqrt(mean_squared_error(y_train, y_predtrain))))
    y_pred=gb.predict(X_test)
    print("Root Mean Squared Error on test data: {}".format(sqrt(mean_squared_error(y_test, y_pred))))
    print("The parameters are: {}".format(bestmd))
    return gb.feature_importances_






