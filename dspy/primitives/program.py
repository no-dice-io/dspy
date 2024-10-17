from typing import Optional

import magicattr

from dsp.modules.lm import LM
import dspy
from dspy.primitives.assertions import *
from dspy.primitives.module import BaseModule
from dspy.primitives.utils import _ERR_MSG_PROGRAM_LM

class ProgramMeta(type):
    pass

class Module(BaseModule, metaclass=ProgramMeta):
    def _base_init(self):
        self._compiled = False

    def __init__(self):
        self._compiled = False

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def set_lm(self, lm: LM):
        """Set the LM for all predictors in the module.

        This is an experimental method, which requires dsp.settings.experimental
        to be enabled.

        Args:
            lm: The LM to set for all predictors.

        Raises:
            AssertionError: If the dspy experimental setting is not enabled.
        """
        # Check if the experimental setting is enabled
        err_msg = _ERR_MSG_PROGRAM_LM
        assert dspy.settings.experimental, err_msg

        # Set the LM for all predictors
        for _, pred in self.named_predictors():
            pred.lm = lm

    def named_predictors(self):
        from dspy.predict.predict import Predict

        return [(name, param) for name, param in self.named_parameters() if isinstance(param, Predict)]

    def predictors(self):
        return [param for _, param in self.named_predictors()]
    
    def set_lm(self, lm):
        import dspy
        assert dspy.settings.experimental, "Setting the lm is an experimental feature."

        for _, param in self.named_predictors():
            param.lm = lm

    def get_lm(self):
        import dspy
        assert dspy.settings.experimental, "Getting the lm is an experimental feature."

        all_used_lms = [param.lm for _, param in self.named_predictors()]

        if len(set(all_used_lms)) == 1:
            return all_used_lms[0]
        
        raise ValueError("Multiple LMs are being used in the module.")

    def __repr__(self):
        s = []

        for name, param in self.named_predictors():
            s.append(f"{name} = {param}")

        return "\n".join(s)

    def map_named_predictors(self, func):
        """Applies a function to all named predictors."""
        for name, predictor in self.named_predictors():
            set_attribute_by_name(self, name, func(predictor))
        return self

    def activate_assertions(self, handler=backtrack_handler, **handler_args):
        """
        Activates assertions for the module.
        The default handler is the backtrack_handler.
        """
        assert_transform_module(self, handler, **handler_args)
        return self

    # def __deepcopy__(self, memo):
    #     # memo is a dict of id's to copies already made during the current call
    #     # Check if the object is already copied
    #     if id(self) in memo:
    #         return memo[id(self)]

    #     print(f"Deep copying {self.__class__.__name__}...")

    #     new_copy = copy.copy(self)
    #     memo[id(self)] = new_copy

    #     for k, v in self.__dict__.items():
    #         print(f"Copying attribute {k} of type {type(v)}...")
    #         setattr(new_copy, k, copy.deepcopy(v, memo))
    #         print("Done")

    #     return new_copy


def set_attribute_by_name(obj, name, value):
    magicattr.set(obj, name, value)

Program = Module
