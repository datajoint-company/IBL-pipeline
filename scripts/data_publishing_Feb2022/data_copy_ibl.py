import datajoint as dj
from datajoint_utilities.dj_data_copy import db_migration

from . import schema_name_mapper

# ------------ DATA COPY -------------

# Set up connection credentials and store config
source_conn = dj.connection.Connection(dj.config['database.host'],
                                       dj.config['database.user'],
                                       dj.config['database.password'])
target_conn = dj.connection.Connection(dj.config['custom']['target_database.host'],
                                       dj.config['custom']['target_database.user'],
                                       dj.config['custom']['target_database.password'])

# Data copy

ibl_acquisition = dj.create_virtual_module('ibl_acquisition', 'ibl_acquisition', connection=source_conn)
ibl_ephys = dj.create_virtual_module('ibl_ephys', 'ibl_ephys', connection=source_conn)

sessions = (ibl_acquisition.Session & ibl_ephys.DefaultCluster).fetch('KEY', limit=10)

table_block_list = {}

batch_size = None


def main():
    for orig_schema_name, cloned_schema_name in schema_name_mapper.items():
        orig_schema = dj.create_virtual_module(orig_schema_name, orig_schema_name, connection=source_conn)
        cloned_schema = dj.create_virtual_module(cloned_schema_name, cloned_schema_name, connection=target_conn)

        db_migration.migrate_schema(orig_schema, cloned_schema,
                                    restriction=sessions,
                                    table_block_list=table_block_list.get(cloned_schema_name, []),
                                    allow_missing_destination_tables=True,
                                    force_fetch=False,
                                    batch_size=batch_size)
