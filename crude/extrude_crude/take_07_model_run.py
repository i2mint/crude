"""
Same as take_04_model_run, but where the dispatch is not as manual.
"""

import os

from crude.extrude_crude.extrude_crude_util import np, apply_model
from crude.extrude_crude.extrude_crude_util import mall as mall_contents

from dol.filesys import mk_tmp_dol_dir
from extrude.crude import KT, StoreName, Mall, mk_mall_of_dill_stores

# def mk_mall(rootdir=None, mall_contents=mall_contents) -> Mall:
#     rootdir = rootdir or mk_tmp_quick_store_dirpath("crude_takes")
#     print(rootdir)
#     mall = dict()
#     for k, store_contents in mall_contents.items():
#         mall[k] = QuickStore(os.path.join(rootdir, k))
#         mall[k].update(store_contents)
#     return mall


# class ReadOnlyDict(dict):
#     def __setitem__(self, k):
#         if k in self:

# mall = mk_mall()
from collections import ChainMap

rootdir = mk_tmp_dol_dir("crude_take_06")
print(rootdir)
# Here we want to use the RAM mall_contents for fvs and fitted_models, but
# a dill mall (persisted) for model_results
ram_stores = mall_contents
persisting_stores = mk_mall_of_dill_stores("model_results", rootdir=rootdir)
mall = dict(mall_contents, **persisting_stores)

# ---------------------------------------------------------------------------------------
# dispatchable function:
from extrude.crude import prepare_for_crude_dispatch

f = prepare_for_crude_dispatch(apply_model, mall)
assert all(
    f("fitted_model_1", "test_fvs") == np.array([[0.0], [1.0], [0.5], [2.25], [-1.5]])
)


def simple_mall_dispatch_core_func(
    key: KT, action: str, store_name: StoreName, mall: Mall
):
    if not store_name:
        # if store_name empty, list the store names (i.e. the mall keys)
        return list(mall)
    else:  # if not, get the store
        store = mall[store_name]

    if action == "list":
        key = key.strip()  # to handle some invisible whitespace that would screw things
        return list(filter(lambda k: key in k, store))
    elif action == "get":
        return store[key]


from enum import Enum


class MallActions(Enum):
    list = "list"
    get = "get"


# TODO: the function doesn't see updates made to mall. Fix.
# Just the partial (with mall set), but without mall arg visible (or will be dispatched)
def explore_mall(key: KT, action: MallActions, store_name: StoreName):
    return simple_mall_dispatch_core_func(key, action, store_name, mall=mall)


# Attempt to do this wit i2.wrapper
# from functools import partial
# from i2.wrapper import remove_params_ingress_factory, wrap
#
# without_mall_param = partial(
#     wrap, ingress=partial(remove_params_ingress_factory, params_to_remove="mall")
# )
# mall_exploration_func = without_mall_param(
#     partial(simple_mall_dispatch_core_func, mall=mall)
# )
# mall_exploration_func.__name__ = "explore_mall"


if __name__ == "__main__":
    from crude.util import ignore_import_problems

    with ignore_import_problems:
        from functools import partial

        class MallActions(Enum):
            list = "list"
            get = "get"

        import streamlit as st
        import streamlit_pydantic as sp
        from streamlitfront.base import dispatch_funcs, BasePageFunc
        from opyratorfront.py2pydantic import func_to_pyd_input_model_cls
        from pydantic import BaseModel, Field

        # TODO: the function doesn't see updates made to mall. Fix.
        # Just the partial (with mall set), but without mall arg visible (or will be
        # dispatched)
        def explore_mall(key: KT, action: MallActions, store_name: StoreName):
            return simple_mall_dispatch_core_func(key, action, store_name, mall=mall)

        def foo(x: str) -> str:
            return x * 2

        dispatchable_apply_model = prepare_for_crude_dispatch(
            apply_model, store_for_param=mall, output_store_name="model_results"
        )
        # extra, to get some defaults in:
        dispatchable_apply_model = partial(
            dispatchable_apply_model,
            fitted_model="fitted_model_1",
            fvs="test_fvs",
        )

        from i2 import name_of_obj

        class SimplePageFuncPydanticWrite(BasePageFunc):
            def __call__(self, state):
                self.prepare_view(state)
                mymodel = func_to_pyd_input_model_cls(self.func)
                name = name_of_obj(self.func)

                data = sp.pydantic_form(key=f"my_form_{name}", model=mymodel)
                # data = sp.pydantic_input(key=f"my_form_{name}", model=mymodel)

                if data:
                    st.write(self.func(**dict(data)))
                    # st.json(data.json())

        configs = {"page_factory": SimplePageFuncPydanticWrite}
        app = dispatch_funcs(
            [foo, dispatchable_apply_model, explore_mall, foo], configs=configs
        )
        app()
