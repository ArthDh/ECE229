import re

import pytest
import pandas as pd
import dash

from dashapp import server

from app.dashapp1.layout import *


# category_df = pd.read_csv(src.config.variables_file)


def test_ui001_sunburst_plot_gives_select_category_prompt(dash_duo):

    app = dash.Dash(__name__)


    app.layout = layout

    dash_duo.start_server(app)



    dash_duo.find_element("#first")
    dash_duo.wait_for_contains_text('#first', "What does your music look like?", timeout=5)


# def test_ui008_sunburst_plot_gives_select_score_prompt(dash_duo):
#     dash_duo.start_server(app)
#     dash_duo.find_element("#expl_continuous_selector span.Select-clear").click()
#     dash_duo.wait_for_contains_text('#sunburst_plot', "Select a score", timeout=5)


# def test_ui002_second_univariate_plot_frequency(dash_duo):
#     dash_duo.start_server(app)
#     dash_duo.wait_for_contains_text('#plot_selector', "frequency plot", timeout=5)

#     dash_duo.select_dcc_dropdown('#expl_category_selector', index=1)
#     dash_duo.wait_for_contains_text('#second_explore_plot', "plotly-logomark", timeout=5)


# def test_ui009_second_univariate_plot_box_gives_select_score_prompt(dash_duo):
#     dash_duo.start_server(app)
#     dash_duo.wait_for_contains_text('#plot_selector', "frequency plot", timeout=5)

#     dash_duo.select_dcc_dropdown('#expl_category_selector', index=1)
#     dash_duo.find_element("#expl_continuous_selector span.Select-clear").click()
#     dash_duo.select_dcc_dropdown('#plot_selector', index=0)
#     dash_duo.wait_for_contains_text('#second_explore_plot', "select a score", timeout=5)


# def test_ui003_second_univariate_plot_box(dash_duo):
#     dash_duo.start_server(app)
#     dash_duo.wait_for_contains_text('#plot_selector', "frequency plot", timeout=5)
#     dash_duo.select_dcc_dropdown('#plot_selector', index=0)

#     short_text = dash_duo.find_element('#expl_continuous_selector').text
#     short_text, _ = re.compile(r"[^a-zA-Z \-']").subn('', short_text)
#     dash_duo.wait_for_contains_text('#second_explore_plot', short_text, timeout=5)


# def test_ui004_histogram_plot(dash_duo):
#     dash_duo.start_server(app)
#     dash_duo.select_dcc_dropdown('#continuous_selector', index=1)
#     dash_duo.wait_for_element('#width_slider', timeout=5)
#     dash_duo.wait_for_element('#hist_plot', timeout=5)


# def test_ui005_four_blocks(dash_duo):
#     dash_duo.start_server(app)
#     dash_duo.wait_for_element('#info-container', timeout=5)


# def test_ui006_report(dash_duo):
#     dash_duo.start_server(app)
#     dash_duo.wait_for_element('#open-xl', timeout=5)
#     dash_duo.wait_for_element('#report', timeout=5)


# def test_ui011_prediction_plot(dash_duo):
#     dash_duo.start_server(app)
#     dash_duo.wait_for_contains_text('#ml_prediction_plot', "Science self-efficacy", timeout=10)