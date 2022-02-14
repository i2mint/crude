"""
Same as take_04_model_run, but where the dispatch is not as manual.
"""

import os
import numpy as np
from dol.filesys import mk_tmp_dol_dir
from extrude.crude import KT, StoreName, Mall, mk_mall_of_dill_stores
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA

# ---------------------------------------------------------------------------------------
# dispatchable function:

def apply_model(fitted_model, fvs, method="transform"):
    method_func = getattr(fitted_model, method)
    return method_func(list(fvs)).tolist()

def learn_model(learner, fvs, method="fit"):
    method_func = getattr(learner, method)
    return method_func(list(fvs))

mall = dict(
    learn_model=dict(MinMaxScaler=MinMaxScaler(),
                     StandardScaler=StandardScaler()),
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

rootdir = mk_tmp_dol_dir("crude_take_06")
print(rootdir)
# Here we want to use the RAM mall_contents for fvs and fitted_models, but
# a dill mall (persisted) for model_results
ram_stores = mall
persisting_stores = mk_mall_of_dill_stores("model_results", rootdir=rootdir)
mall = dict(mall, **persisting_stores)

# POC to dispatch store
def simple_mall_dispatch_core_func(
    key: KT, action: str, store_name: StoreName, mall: Mall
):
    if not store_name:
        # if store_name empty, list the store names (i.e. the mall keys)
        return list(mall)
    else:  # if not, get the store
        store = mall[store_name]

    if action == "list" or not action:
        key = key.strip()  # to handle some invisible whitespace that would screw things
        return list(filter(lambda k: key in k, store))
    elif action == "get":
        return store[key]


# TODO: the function doesn't see updates made to mall. Fix.
# Just the partial (with mall set), but without mall arg visible (or will be dispatched)
def explore_mall(key: KT, action: str, store_name: StoreName):
    return simple_mall_dispatch_core_func(key, action, store_name, mall=mall)



if __name__ == "__main__":
    from extrude.crude import prepare_for_crude_dispatch
    from streamlitfront.base import dispatch_funcs
    from functools import partial

    dispatchable_learn_model = prepare_for_crude_dispatch(
        learn_model, store_for_param=mall, output_store="fitted_model"
    )
    dispatchable_apply_model = prepare_for_crude_dispatch(
        apply_model, store_for_param=mall, output_store="model_results"
    )

    dispatchable_learn_model = partial(
        dispatchable_learn_model,
        learner="StandardScaler",
        fvs="test_fvs",
    )

    # extra, to get some defaults in:
    dispatchable_apply_model = partial(
        dispatchable_apply_model,
        fitted_model="fitted_model_1",
        fvs="test_fvs",
    )
    app = dispatch_funcs([dispatchable_apply_model, dispatchable_learn_model, explore_mall])
    app()
