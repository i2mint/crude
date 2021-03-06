"""
Same as take_04_model_run, but where the dispatch is not as manual.
"""

import numpy as np
from front.crude import KT, StoreName, Mall
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from omodel.outliers.pystroll import OutlierModel as Stroll


# ---------------------------------------------------------------------------------------
# dispatchable function:


def apply_model(fitted_model, fvs, method="transform"):
    method_func = getattr(fitted_model, method)
    return method_func(list(fvs)).tolist()


def learn_model(learner, fvs, method="fit"):
    method_func = getattr(learner, method)
    return method_func(list(fvs))


def parametrize_and_save_pca(n_components: int):
    return PCA(n_components=n_components, random_state=None)


def parametrize_and_save_stroll(n_components: int):
    return Stroll(n_components=n_components)


mall = dict(
    learner=dict(MinMaxScaler=MinMaxScaler(), StandardScaler=StandardScaler()),
    fvs=dict(  # Mapping[FVsKey, FVs]
        train_fvs_1=np.array([[1], [2], [3], [5], [4], [2], [1], [4], [3]]),
        train_fvs_2=np.array([[1], [10], [5], [3], [4]]),
        test_fvs=np.array([[1], [5], [3], [10], [-5]]),
    ),
    fitted_model=dict(
        fitted_model_1=MinMaxScaler().fit(
            [[1], [2], [3], [5], [4], [2], [1], [4], [3]]
        ),
        fitted_model_2=MinMaxScaler().fit([[1], [10], [5], [3], [4]]),
    ),
    model_results=dict(),
)


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
    from front.crude import prepare_for_crude_dispatch
    from streamlitfront.base import dispatch_funcs
    from functools import partial

    dispatchable_learn_model = prepare_for_crude_dispatch(
        learn_model,
        param_to_mall_map=dict(learner="learner", fvs="fvs"),
        mall=mall,
        output_store="fitted_model",
    )

    dispatchable_learn_model = partial(
        dispatchable_learn_model,
        learner="StandardScaler",
        fvs="test_fvs",
    )

    dispatchable_apply_model = prepare_for_crude_dispatch(
        apply_model,
        param_to_mall_map=dict(fitted_model="fitted_model", fvs="fvs"),
        mall=mall,
        output_store="model_results",
        save_name_param="save_name_for_apply_model",
    )

    dispatchable_apply_model = partial(
        dispatchable_apply_model,
        fitted_model="fitted_model_1",
        fvs="test_fvs",
    )

    dispatchable_parametrize_and_save_pca = prepare_for_crude_dispatch(
        parametrize_and_save_pca,
        mall=mall,
        output_store="learner",
        save_name_param="name_for_unfitted_model",
    )

    dispatchable_parametrize_and_save_pca = partial(
        dispatchable_parametrize_and_save_pca, n_components=5
    )

    dispatchable_parametrize_and_save_stroll = prepare_for_crude_dispatch(
        parametrize_and_save_stroll,
        mall=mall,
        output_store="learner",
        save_name_param="name_for_unfitted_model",
    )

    dispatchable_parametrize_and_save_stroll = partial(
        dispatchable_parametrize_and_save_stroll, n_components=5
    )

    app = dispatch_funcs(
        [
            dispatchable_apply_model,
            dispatchable_parametrize_and_save_pca,
            dispatchable_parametrize_and_save_stroll,
            dispatchable_learn_model,
            explore_mall,
        ]
    )
    app()
