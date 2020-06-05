import numpy as np

from .base import (sklearn_regression,
                   sklearn_regression_lagrange,
                   sklearn_classifier,
                   sklearn_classifier_lagrange)

from ..smooth.glm import (glm, 
                          cloglog_loglike)

class sklearn_cloglog(sklearn_regression):

    """

    A simple regression mixin for sklearn
    that allows any atom to be used as a regularizer.

    """

    def _loglike_factory(self, X, y):
        response, case_weights_, offset_ = self._check_y_arg(y)

        if response.ndim == 2:
            successes = response[:,0]
            trials = response[:,1]
        else:
            successes = response
            trials = None

        return glm.cloglog(X, 
                           successes,
                           trials=trials,
                           case_weights=case_weights_,
                           coef=self.coef,
                           saturated_offset=offset_)

    def _saturated_score(self,
                         predictions,
                         response,
                         case_weights=None):
        
        if response.ndim == 2:
            successes = response[:,0]
            trials = response[:,1]
        else:
            successes = response
            trials = None

        loss = lambda yhat: cloglog_loglike(successes.shape,
                                            successes,
                                            trials=trials,
                                            case_weights=case_weights).smooth_objective(yhat, 'func')

        if self.score_method == 'deviance':
            return np.sum(loss(predictions))
        elif self.score_method == 'mean_deviance':
            return np.mean(loss(predictions))
        elif self.score_method == 'R2':
            SSE = np.sum(loss(predictions))
            SST = np.sum(loss(response.mean() * np.ones_like(response)))
            return 1 - SSE / SST
        elif self.score_method == 'accuracy':
            labels = predictions > 0
            return np.mean(labels == response)
        else:
            return np.nan

class sklearn_cloglog_lagrange(sklearn_regression_lagrange, sklearn_cloglog):
    pass

class sklearn_cloglog_classifier(sklearn_classifier):

    """

    A simple regression mixin for sklearn
    that allows any atom to be used as a regularizer.

    """

    def _loglike_factory(self, X, y):
        response, case_weights_, offset_ = self._check_y_arg(y)

        if response.ndim == 2:
            successes = response[:,0]
            trials = response[:,1]
        else:
            successes = response
            trials = None

        return glm.cloglog(X, 
                           successes,
                           trials=trials,
                           case_weights=case_weights_,
                           coef=self.coef,
                           saturated_offset=offset_)

    def _saturated_score(self,
                         predictions,
                         response,
                         case_weights=None):
        
        if response.ndim == 2:
            successes = response[:,0]
            trials = response[:,1]
        else:
            successes = response
            trials = None

        if self.score_method == 'accuracy':
            return np.mean(predictions == successes)
        return np.nan

    def predict_proba(self, X):
        """
        Predict new probabilities in classification setting.

        Parameters
        ----------

        X : np.ndarray((n, p))
            Feature matrix.

        Returns
        -------

        probs : np.ndarray(n)
            Predictions from classification model.

        """
        linpred = X.dot(self._coefs)
        exp_lin = np.exp(linpred)
        return exp_lin / (1 + exp_lin)

class sklearn_cloglog_classifier_lagrange(sklearn_cloglog_classifier):
    pass

