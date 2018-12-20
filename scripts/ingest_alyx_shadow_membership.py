#! /usr/bin/env python3

'''
This script inserts membership tuples into the membership shadow tables, \
which cannot be inserted with auto-population.
'''
import datajoint as dj
from ibl_pipeline.ingest import alyxraw, reference, subject, action, acquisition, data
from ibl_pipeline.ingest import get_raw_field as grf


# reference.ProjectLabMember
keys = (alyxraw.AlyxRaw & 'model="subjects.project"').proj(project_uuid='uuid')

for key in keys:
    key_p = dict()
    key_p['project_name'] = (reference.Project & key).fetch1('project_name')

    user_uuids = grf(key, 'users', multiple_entries=True)

    for user_uuid in user_uuids:
        key_pl = key_p.copy()
        key_pl['user_name'] = (reference.LabMember & 'user_uuid="{}"'.format(user_uuid)).fetch1('user_name')
        reference.ProjectLabMember.insert1(key_pl, skip_duplicates=True)


# subject.AlleleSequence
keys = (alyxraw.AlyxRaw & 'model="subjects.allele"').proj(allele_uuid='uuid')
for key in keys:
    key_a = dict()
    key_a['allele_name'] = (subject.Allele & key).fetch1('allele_name')
    key['uuid'] = key['allele_uuid']
    sequences = grf(key, 'sequences', multiple_entries=True)
    for sequence in sequences:
        if sequence != 'None':
            key_as = key_a.copy()
            key_as['sequence_name'] = (subject.Sequence & 'sequence_uuid="{}"'.format(sequence)).fetch1('sequence_name')
            subject.AlleleSequence.insert1(key_as, skip_duplicates=True)

# subject.LineAllele
keys = (alyxraw.AlyxRaw & 'model="subjects.line"').proj(line_uuid='uuid')
for key in keys:
    key_l = dict()
    key_l['binomial'], key_l['line_name'] = (subject.Line & key).fetch1('binomial', 'line_name')
    key['uuid'] = key['line_uuid']
    alleles = grf(key, 'alleles', multiple_entries=True)

    for allele in alleles:
        if allele != 'None':
            key_la = key_l.copy()
            key_la['allele_name'] = (subject.Allele & 'allele_uuid="{}"'.format(allele)).fetch1('allele_name')
            subject.LineAllele.insert1(key_la, skip_duplicates=True)

# action.SurgeryLabMember
keys = (alyxraw.AlyxRaw & 'model = "actions.surgery"').proj(surgery_uuid='uuid')
for key in keys:
    key_s = dict()
    key_s['subject_uuid'], key_s['surgery_start_time'] = (action.Surgery & key).fetch1('subject_uuid', 'surgery_start_time')
    key['uuid'] = key['surgery_uuid']
    user_uuids = grf(key, 'users', multiple_entries=True)

    for user_uuid in user_uuids:
        if user_uuid != 'None':
            key_sl = key_s.copy()
            key_sl['user_name'] = (reference.LabMember & 'user_uuid="{}"'.format(user_uuid)).fetch1('user_name')
            action.SurgeryLabMember.insert1(key_sl, skip_duplicates=True)

# action.SurgeryProcedure
keys = (alyxraw.AlyxRaw & 'model = "actions.surgery"').proj(surgery_uuid='uuid')
for key in keys:
    key_s = dict()
    key_s['subject_uuid'], key_s['surgery_start_time'] = (action.Surgery & key).fetch1('subject_uuid', 'surgery_start_time')
    key['uuid'] = key['surgery_uuid']
    procedures = grf(key, 'procedures', multiple_entries=True)

    for procedure in procedures:
        if procedure != 'None':
            key_sp = key_s.copy()
            key_sp['procedure_type_name'] = (action.ProcedureType & 'procedure_type_uuid="{}"'.format(procedure)).fetch1('procedure_type_name')
            action.SurgeryProcedure.insert1(key_sp, skip_duplicates=True)

# acquisition.ChildSession
keys = (alyxraw.AlyxRaw & 'model="actions.session"').proj(session_uuid='uuid')
for key in keys:
    key_cs = dict()
    key['uuid'] = key['session_uuid']

    key_cs['subject_uuid'], key_cs['session_start_time'] = \
        (acquisition.Session & key).fetch1('subject_uuid', 'session_start_time')

    parent_session = grf(key, 'parent_session')
    if parent_session != 'None':
        key_cs['parent_session_start_time'] = \
            (acquisition.Session & 'session_uuid="{}"'.format(parent_session)).fetch1('session_start_time')
        acquisition.ChildSession.insert1(key_cs, skip_duplicates=True)

# acquisition.SessionLabMember
keys = (alyxraw.AlyxRaw & 'model = "actions.Session"').proj(session_uuid = 'uuid')
for key in keys:
    key_s = dict()
    key['uuid'] = key['session_uuid']
    key_s['subject_uuid'], key_s['session_start_time'] = \
        (acquisition.Session & key).fetch1('subject_uuid', 'session_start_time')

    user_uuids = grf(key, 'users', multiple_entries=True)

    for user_uuid in user_uuids:
        if user_uuid != 'None':
            key_su = key_s.copy()
            key_su['user_name'] = (reference.LabMember & 'user_uuid="{}"'.format(user_uuid)).fetch1('user_name')
            acquisition.SessionLabMember.insert1(key_su, skip_duplicates=True)

# acquisition.SessionProcedureType
keys = (alyxraw.AlyxRaw & 'model = "actions.Session"').proj(session_uuid = 'uuid')
for key in keys:
    key_s = dict()
    key['uuid'] = key['session_uuid']

    key_s['subject_uuid'], key_s['session_start_time'] = \
        (acquisition.Session & key).fetch1('subject_uuid', 'session_start_time')

    procedures = grf(key, 'procedures', multiple_entries=True)

    for procedure in procedures:
        if procedure != 'None':
            key_sp = key_s.copy()
            key_sp['procedure_type_name'] = (action.ProcedureType & 'procedure_type_uuid="{}"'.format(procedure)).fetch1('procedure_type_name')
            acquisition.SessionProcedureType.insert1(key_sp, skip_duplicates=True)

# data.ProjectRepository
keys = (alyxraw.AlyxRaw & 'model="subjects.project"').proj(project_uuid='uuid')
for key in keys:
    key_p = dict()
    key_p['project_name'] = (reference.Project & key).fetch1('project_name')
    key['uuid'] = key['project_uuid']

    repo_uuids = grf(key, 'repositories', multiple_entries=True)

    for repo_uuid in repo_uuids:
        if repo_uuid != 'None':
            key_pr = key_p.copy()
            key_pr['repo_name'] = (data.DataRepository & 'repo_uuid="{}"'.format(repo_uuid)).fetch1('repo_name')
            data.ProjectRepository.insert1(key_pr, skip_duplicates=True)
