"""
An example of how to transform (manually) a function that runs some data through a model
(both too complex to enter directly and explicitly in forms) into a streamlit
dispatchable function that uses a store (a Mapping) to manage complex data.
"""

# This is what we want our "dispatchable" wrapper to look like

# There should be real physical stores for those types (FVs, FittedModel) that need them
from typing import Any

FVs = Any
FittedModel = Any

# ---------------------------------------------------------------------------------------
# The function(ality) we want to dispatch:
def apply_model(fitted_model: FittedModel, fvs: FVs, method="transform"):
    method_func = getattr(fitted_model, method)
    return method_func(list(fvs)).tolist()


# ---------------------------------------------------------------------------------------
# The stores that will be used -- here, all stores are just dictionaries, but the
# contract is with the typing.Mapping (read-only here) interface.

from crude.examples.buildup.buildup_utils import mall, np

# ---------------------------------------------------------------------------------------
# dispatchable function:

from crude.base import auto_key


def prepare_for_dispatch(func):
    """Wrap func into something that is ready for dispatch.
    In real live, apply_model_using_stores will be made automatically by wrapping
    apply_model.
    Here is manual, but we're pretending that this wrapping happens automatically...
    """
    # apply_model_using_stores will be made automatically by wrapping apply_model
    # Here we're just pretending that this wrapping happens automatically
    if func.__name__ == "apply_model":

        def apply_model_using_stores(
            fitted_model: str,
            fvs: str,
            method: str = "transform",
            # TODO: Have streamlit populate automatically with auto_key:
            save_name: str = "",
        ):
            # make a name if not given explicitly
            save_name = save_name or auto_key(fitted_model=fitted_model, fvs=fvs)
            # get the inputs
            fitted_model = mall["fitted_model"][fitted_model]
            fvs = mall["fvs"][fvs]
            # compute the function
            result = apply_model(fitted_model, fvs, method=method)
            # store the outputs
            mall["model_results"][save_name] = result

            return result  # or not

        # sanity check: test apply_model_using_stores
        assert list(mall["model_results"]) == []
        t = apply_model_using_stores(fitted_model="fitted_model_1", fvs="test_fvs")
        print(list(mall["model_results"]))
        assert list(mall["model_results"]) == [
            "fitted_model=fitted_model_1,fvs=test_fvs"
        ]
        assert all(t == np.array([[0.0], [1.0], [0.5], [2.25], [-1.5]]))
        mall["model_results"].clear()

        return apply_model_using_stores
    else:
        raise ValueError(f"Can't dispatch {func}")


if __name__ == "__main__":
    from crude.util import ignore_import_problems

    with ignore_import_problems:
        from streamlitfront.base import dispatch_funcs

        funcs = [prepare_for_dispatch(apply_model)]
        dispatch_funcs(funcs)
        # app = dispatch_funcs(funcs, {'style': {'root_dir': os.path.dirname(os.path.realpath(__file__))}})
        # app.run_server(debug=True)
