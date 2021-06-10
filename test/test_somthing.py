from unittest import TestCase
import numpy as np
import pandas as pd



# make_prediction_plot = make_prediction_plot.__wrapped__


class TestMultivariateMethods(TestCase):

    
    def test_get_feature_importance(self):
        from app.util.data_callbacks import get_my_id
        res = get_my_id()
        assert isinstance(res, str)

if __name__ == '__main__':
    unittest.main()