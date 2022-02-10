"""Utils for buildup"""

from typing import Any
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
import numpy as np

# Being lazy with the definition of these:
FVs = Any
FittedModel = Any
Learner = Any

# ---------------------------------------------------------------------------------------
# The function(ality) we want to dispatch:
# Note: apply_model and learn_model both have the same structure, just different
#  parameters (names, annotations, defaults).
# TODO: apply_model and learn_model both have the same structure, just different
#  parameters (names, annotations, defaults), so...
#  Could make them from i2.wrapper tools. Should is a diffrent question though.


def apply_model(fitted_model: FittedModel, fvs: FVs, method="transform"):
    method_func = getattr(fitted_model, method)
    # TODO: Should remove .tolist() (and possibly the list of list(fvs)).
    #  Not concern here.
    return method_func(list(fvs)).tolist()


def learn_model(learner: Learner, fvs: FVs, method="fit"):
    method_func = getattr(learner, method)
    return method_func(list(fvs))


# TODO: Make a sklearn-free and numpy-free version?
# class MinMaxScaler:
#     def fit(self, X):
#         self.min_ = min(X)

# ---------------------------------------------------------------------------------------
# The stores that will be used -- here, all stores are just dictionaries, but the
# contract is with the typing.Mapping (read-only here) interface.
# As we grow up, we'll use other mappings, such as:
# - server side RAM (as done here, simply)
# - server side persistence (files or any DB or file system thanks to the dol package)
# - computation (when you want the request for a key to actually launch a process that
#   will generate the value for you (some say you should be obvious to that detail))
# - client side RAM (when we figure that out)

# really, should be a str from a list of options, given by list(fvs_store)
FVsKey = str
# really, should be a str from a list of options, given by list(fitted_model_store)
FittedModelKey = str
Result = Any
ResultKey = str

mall = dict(
    fvs=dict(  # Mapping[FVsKey, FVs]
        train_fvs_1=np.array([[1], [2], [3], [5], [4], [2], [1], [4], [3]]),
        train_fvs_2=np.array([[1], [10], [5], [3], [4]]),
        test_fvs=np.array([[1], [5], [3], [10], [-5]]),
    ),
    fitted_model=dict(  # Mapping[FittedModelKey, FittedModel]
        fitted_model_1=MinMaxScaler().fit(
            [[1], [2], [3], [5], [4], [2], [1], [4], [3]]
        ),
        fitted_model_2=MinMaxScaler().fit([[1], [10], [5], [3], [4]]),
    ),
    model_results=dict(),  # Mapping[ResultKey, Result]
)

mall_with_learners = dict(
    mall,
    **dict(
        MinMaxScaler=MinMaxScaler(),
        StandardScaler=StandardScaler(),
        PCA=PCA(),
    )

)