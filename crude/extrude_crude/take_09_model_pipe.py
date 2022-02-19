"""
Same as take_06_model_run, with additionally:
- dispatching learn_model
- introducing iterable_to_enum, inject_enum_annotations (from from front.util)

"""

import os

from crude.extrude_crude.extrude_crude_util import (
    apply_model,
    learn_model,
    test_dispatch,
    mall_with_learners as mall_contents,
    get_a_root_directory_for_module_and_mk_tmp_dir_for_it
)

from front.crude import KT, StoreName, Mall, mk_mall_of_dill_stores

rootdir = get_a_root_directory_for_module_and_mk_tmp_dir_for_it(__file__)

# Here we want to use the RAM mall_contents for fvs and fitted_models, but
# a dill mall (persisted) for model_results
# ram_stores = mall_contents
persisting_stores = mk_mall_of_dill_stores(
    ["model_results", "learn_store"],
    rootdir=rootdir
)
mall = dict(mall_contents, **persisting_stores)

# ---------------------------------------------------------------------------------------
# dispatchable function:
from front.crude import prepare_for_crude_dispatch
from front.crude import simple_mall_dispatch_core_func
from front.util import inject_enum_annotations
from front.base import prepare_for_dispatch

# TODO: Conditional Enums: Selection list of one field based on selection of previous
# TODO: Deal with long Enums (paging? filtering?)
# TODO: Enhanced Enum; Give more info to user to be able to choose

# TODO: Better dispatching of mall explorer (needs conditional Enums)
@inject_enum_annotations(action=["list", "get"], store_name=mall)
def explore_mall(
    store_name: StoreName,
    key: KT,
    action: str,
):
    return simple_mall_dispatch_core_func(key, action, store_name, mall=mall)

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from front.util import partialx

# TODO: Again, need for conditional fields
# TODO: Auto-suggestions and/or resolution of arg problems
# TODO: Find more systematic and automatic way to deal with arg names conflicting with
#  Pydantic
dispatchable_min_max_scaler = prepare_for_dispatch(
    partialx(MinMaxScaler, copy=True, rm_partialize=True),
    output_store=mall["learner_store"],
)

dispatchable_standard_scaler = prepare_for_dispatch(
    partialx(StandardScaler, copy=True, rm_partialize=True),
    output_store=mall["learner_store"],
)

dispatchable_pca = prepare_for_dispatch(
    partialx(PCA, copy=True, rm_partialize=True), output_store=mall["learner_store"],
)

# TODO: param_to_mall_map maker (from list of strings or pairs thereof)
# TODO: automatic mall store enhancer
# TODO: Automatic output_store maker from DAG
# TODO: Automatic defaults from Enum (do the defaults even interact well with Enums?)
dispatchable_learn_model = prepare_for_dispatch(
    learn_model,
    param_to_mall_map={"learner": "learner_store", "fvs": "fvs"},
    mall=mall,
    output_store="fitted_model",
    defaults=dict(
        learner='StandardScaler',
        fvs="train_fvs_1",
    )
)

dispatchable_apply_model = prepare_for_dispatch(
    apply_model,
    param_to_mall_map=["fvs", "fitted_model"],
    mall=mall,
    output_store="model_results",
    defaults=dict(
        fitted_model="fitted_model_1",
        fvs="test_fvs",
    )
)


if __name__ == "__main__":
    from streamlitfront.base import dispatch_funcs
    from streamlitfront.page_funcs import SimplePageFuncPydanticWrite

    configs = {"page_factory": SimplePageFuncPydanticWrite}

    app = dispatch_funcs(
        [dispatchable_min_max_scaler, dispatchable_standard_scaler, dispatchable_pca]
        + [dispatchable_learn_model, dispatchable_apply_model]
        + [explore_mall],
        configs=configs,
    )
    # print(app)
    print(app)
    print(__file__)
    app()


