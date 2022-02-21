import datajoint as dj
from datajoint_utilities.dj_data_copy.pipeline_cloning import ClonedPipeline

from . import schema_name_mapper, source_db_prefix


def clone_ibl_pipeline():
    ibl_behavior = dj.create_virtual_module('ibl_behavior', source_db_prefix + 'ibl_behavior')
    ibl_ephys = dj.create_virtual_module('ibl_ephys', source_db_prefix + 'ibl_ephys')

    diagram = dj.Diagram(ibl_behavior.CompleteTrialSession) + dj.Diagram(ibl_ephys.AlignedTrialSpikes)

    cloned_pipeline = ClonedPipeline(diagram, schema_name_mapper, verbose=True)

    cloned_pipeline.save_code(save_dir=f'./cloned_pipelines/{target_db_prefix}')
