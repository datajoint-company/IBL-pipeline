import datajoint as dj

assert 'custom' in dj.config

assert 'target_database.host' in dj.config['custom']
assert 'target_database.user' in dj.config['custom']
assert 'target_database.password' in dj.config['custom']
assert 'target_database.db_prefix' in dj.config['custom']

source_db_prefix = dj.config['database.prefix']
target_db_prefix = dj.config['custom']['target_database.db_prefix']

schema_name_mapper = {source_db_prefix + schema_name: target_db_prefix + schema_name
                      for schema_name in ('ibl_reference',
                                          'ibl_subject',
                                          'ibl_action',
                                          'ibl_data',
                                          'ibl_acquisition',
                                          'ibl_behavior',
                                          'ibl_analyses_behavior',
                                          'ibl_ephys',
                                          'ibl_histology')}
