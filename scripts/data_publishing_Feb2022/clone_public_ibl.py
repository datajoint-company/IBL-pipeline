import datajoint as dj
from datajoint_utilities.dj_data_copy.pipeline_cloning import ClonedPipeline

from . import schema_name_mapper, source_db_prefix, target_db_prefix


def clone_public_ibl_pipeline():
    ibl_acquisition = dj.create_virtual_module('ibl_acquisition', source_db_prefix + 'ibl_acquisition')
    ibl_action = dj.create_virtual_module('ibl_action', source_db_prefix + 'ibl_action')
    ibl_analyses_behavior = dj.create_virtual_module('ibl_analyses_behavior', source_db_prefix + 'ibl_analyses_behavior')
    ibl_behavior = dj.create_virtual_module('ibl_behavior', source_db_prefix + 'ibl_behavior')
    ibl_data = dj.create_virtual_module('ibl_data', source_db_prefix + 'ibl_data')
    ibl_ephys = dj.create_virtual_module('ibl_ephys', source_db_prefix + 'ibl_ephys')
    ibl_subject = dj.create_virtual_module('ibl_subject', source_db_prefix + 'ibl_subject')
    ibl_histology = dj.create_virtual_module('ibl_histology', source_db_prefix + 'ibl_histology')
    ibl_reference = dj.create_virtual_module('ibl_reference', source_db_prefix + 'ibl_reference')

    diagram = (
        dj.Diagram(ibl_acquisition)
        + dj.Diagram(ibl_action)
        + dj.Diagram(ibl_analyses_behavior)
        + dj.Diagram(ibl_behavior)
        + dj.Diagram(ibl_data)
        + dj.Diagram(ibl_ephys)
        + dj.Diagram(ibl_subject)
        + dj.Diagram(ibl_histology)
        + dj.Diagram(ibl_reference)
    )

    cloned_pipeline = ClonedPipeline(diagram, schema_name_mapper, verbose=True)

    cloned_pipeline.save_code(save_dir=f'./cloned_pipelines/{target_db_prefix}')
