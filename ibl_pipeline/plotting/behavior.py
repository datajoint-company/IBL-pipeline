import datajoint as dj
from ..analyses import behavior
from .. import subject, action
import numpy as np
import pandas as pd
from ..utils import psychofit as psy
import plotly
import plotly.graph_objs as go
import statsmodels.stats.proportion as smp

schema = dj.schema('ibl_plotting_behavior')


@schema
class SessionPsychCurve(dj.Computed):
    definition = """
    -> behavior.PsychResults
    ---
    plotting_data:  longblob     # dictionary for the plotting info
    """

    def make(self, key):
        contrasts, prob_right, \
            threshold, bias, lapse_low, lapse_high, \
            n_trials, n_trials_right = (behavior.PsychResults & key).fetch1(
                'signed_contrasts', 'prob_choose_right',
                'threshold', 'bias', 'lapse_low', 'lapse_high',
                'n_trials_stim', 'n_trials_stim_right')
        pars = [bias, threshold, lapse_low, lapse_high]
        contrasts = contrasts * 100
        contrasts_fit = np.arange(-100, 100)
        prob_right_fit = psy.erf_psycho_2gammas(pars, contrasts_fit)

        ci = smp.proportion_confint(
            n_trials_right, n_trials,
            alpha=0.032, method='normal') - prob_right

        behavior_data = dict(
            x=contrasts.tolist(),
            y=prob_right.tolist(),
            error_y=dict(
                type='data',
                array=ci[0].tolist(),
                arrayminus=np.negative(ci[1]).tolist(),
                visible=True
                ),
            mode='markers',
            name='data'
        )

        behavior_fit = dict(
            x=contrasts_fit.tolist(),
            y=prob_right_fit.tolist(),
            name='model fits'
        )

        data = [behavior_data, behavior_fit]
        layout = go.Layout(
            width=600,
            height=400,
            title='Psychometric Curve',
            xaxis={'title': 'Contrast(%)'},
            yaxis={'title': 'Probability choose right'}
        )

        fig = go.Figure(data=[go.Scatter(behavior_data),
                              go.Scatter(behavior_fit)], layout=layout)

        key['plotting_data'] = fig.to_plotly_json()
        self.insert1(key)


@schema
class WaterWeight(dj.Computed):
    definition = """
    -> subject.Subject
    water_weight_date:   date    # last date of water weight
    ---
    plotting_data:  longblob     # dictionary for the plotting info
    """

    key_source = dj.U('subject_uuid', 'water_weight_date') & \
        subject.Subject.aggr(
            action.Weighing * action.WaterAdministration,
            water_weight_date='DATE(GREATEST(MAX(weighing_time), \
                MAX(administration_time)))'
        )

    def make(self, key):
        subj = subject.Subject & key

        water_info_query = (action.WaterAdministration & subj).proj(
            'water_administered', 'watertype_name',
            water_date='DATE(administration_time)')
        water_info = pd.DataFrame(water_info_query.fetch(as_dict=True))
        water_types = water_info.watertype_name.unique()
        water_info.pop('administration_time')
        water_info.pop('subject_uuid')
        water_info_type = water_info.pivot_table(
            index='water_date', columns='watertype_name',
            values='water_administered', aggfunc='sum')

        weight_info_query = (action.Weighing & subj).proj(
            'weight', weighing_date='DATE(weighing_time)')

        weight_info = pd.DataFrame(
            weight_info_query.fetch(as_dict=True))
        weight_info.pop('subject_uuid')
        weight_info.pop('weighing_time')
        weight_info.pivot_table(index='weighing_date', values='weight')

        data = [
            go.Bar(
                x=[t.strftime('%Y-%m-%d')
                    for t in water_info_type.index.tolist()],
                y=water_info_type[water_type].tolist(),
                name=water_type,
                yaxis='y1')
            for water_type in water_types
        ]

        data.append(
            go.Scatter(
                x=[t.strftime('%Y-%m-%d')
                    for t in weight_info['weighing_date'].tolist()],
                y=weight_info['weight'].tolist(),
                mode='lines+markers',
                name='Weight',
                marker=dict(
                    size=6,
                    color='black'),
                yaxis='y2'
            ))

        layout = go.Layout(
            yaxis=dict(
                title='Water intake (mL)'),
            yaxis2=dict(
                title='Weight (g)',
                overlaying='y',
                side='right'
            ),
            width=600,
            height=400,
            title='Water intake and weight',
            xaxis=dict(title='Date'),
            legend=dict(
                x=0,
                y=1.2,
                orientation='h')
        )
        fig = go.Figure(data=data, layout=layout)
        key['plotting_data'] = fig.to_plotly_json()
        self.insert1(key)
