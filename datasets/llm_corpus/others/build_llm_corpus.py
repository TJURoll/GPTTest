import argparse
import collections
import csv
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import re
from string import Formatter

import numpy as np
import pyarrow.parquet as parquet
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
import selfies


BASE = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE / 'FG26_query_response_templates_expand.json'
SEED = 20260913
SCALAR_TASKS = ['homo_energy', 'lumo_energy', 'dipole_magnitude', 'isotropic_polarizability']
FG_TASK = 'functional_group_motifs_positive_identification'
FORBIDDEN = re.compile(r'[:：{}]|\b(?:cif|xyz|files?|placeholder|gap|SCF)\b|system prompt', re.I)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    temporary = Path(str(path) + '.partial')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def load_templates():
    return json.loads(TEMPLATE_PATH.read_text())


def load_records(templates, validate_graphs=False):
    for source_path, expected_hash in templates['source_sha256'].items():
        require(file_sha256(source_path) == expected_hash, f'Template source hash changed {source_path}')
    selection = templates['record_selection']
    records = {}
    with open(selection['authority_path']) as stream:
        for line in stream:
            source = json.loads(line)
            record_index = source['record_index']
            require(record_index not in records, 'Duplicate authority record')
            records[record_index] = {field: source[field] for field in
                                     ['record_index', 'canonical_smiles', 'canonical_selfies', 'selfies_policy']}
    split_seen = set()
    with open(selection['split_path']) as stream:
        for line in stream:
            source = json.loads(line)
            record_index = source['record_index']
            require(record_index in records and record_index not in split_seen, 'Invalid split membership')
            require(source['split'] in ['train', 'val'], 'Invalid split label')
            records[record_index]['split'] = source['split']
            split_seen.add(record_index)
    require(split_seen == set(records), 'Incomplete split map')
    labels = templates['functional_group_policy']['active_labels']
    numeric_fields = [field for field, rule in templates['numeric_format'].items() if isinstance(rule, dict)]
    metadata_seen = set()
    key_map = {}
    for row in csv.DictReader(open(selection['metadata_path'])):
        record_index = int(row['record_index'])
        if record_index not in records:
            continue
        require(record_index not in metadata_seen and row['key_id'] not in key_map, 'Duplicate metadata identity')
        record = records[record_index]
        molecule = Chem.MolFromSmiles(row['canonical_smiles'])
        require(molecule is not None, f'Invalid molecule {record_index}')
        require(Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=False) == record['canonical_smiles'],
                f'Metadata graph mismatch {record_index}')
        require(rdMolDescriptors.CalcMolFormula(molecule) == row['formula'], f'Formula mismatch {record_index}')
        require(row['aromatic'] in ['0', '1'], 'Invalid aromatic value')
        require(any(atom.GetIsAromatic() for atom in molecule.GetAtoms()) == bool(int(row['aromatic'])),
                f'Aromatic mismatch {record_index}')
        require(all(row['fg_' + label] in ['0', '1'] for label in labels), 'Invalid FG labels')
        for field in numeric_fields:
            record[field] = row[field] if field == 'formula' else float(row[field])
            if field != 'formula':
                require(math.isfinite(record[field]), f'Nonfinite {field}')
        record.update(key_id=row['key_id'], aromatic=int(row['aromatic']), n_atoms=int(row['n_atoms']),
                      positive_fg_labels=[label for label in labels if row['fg_' + label] == '1'],
                      elements=sorted({atom.GetSymbol() for atom in Chem.AddHs(molecule).GetAtoms()}))
        if validate_graphs:
            target = record['canonical_selfies']
            require(target and not re.search(r'\s|[:：@{}]', target), f'Invalid SELFIES text {record_index}')
            decoded = Chem.MolFromSmiles(selfies.decoder(target))
            require(decoded is not None and Chem.MolToSmiles(decoded, canonical=True, isomericSmiles=False)
                    == record['canonical_smiles'], f'SELFIES graph mismatch {record_index}')
        key_map[row['key_id']] = record_index
        metadata_seen.add(record_index)
    require(metadata_seen == set(records), 'Incomplete metadata join')
    geometry_seen = set()
    with (BASE / 'structure_index.jsonl').open() as stream:
        for line in stream:
            source = json.loads(line)
            record_index = source['record_index']
            require(record_index in records and record_index not in geometry_seen, 'Unexpected structure index')
            record = records[record_index]
            for field in ['key_id', 'split', 'formula', 'n_atoms']:
                require(record[field] == source[field], f'Structure index {field} mismatch {record_index}')
            for field in numeric_fields:
                if field != 'formula':
                    require(record[field] == source['values'][field], f'Property join mismatch {record_index}')
            for field in ['input_xyz_path', 'input_xyz_relative_path', 'input_xyz_sha256', 'calculation']:
                record[field] = source[field]
            geometry_seen.add(record_index)
    require(geometry_seen == set(records), 'Incomplete structure index')
    require(len(records) == selection['authority_records'], 'Wrong authority count')
    require(dict(collections.Counter(record['split'] for record in records.values())) == selection['split_counts'],
            'Split count mismatch')
    graph_splits = {}
    for record in records.values():
        graph = record['canonical_smiles']
        require(graph_splits.setdefault(graph, record['split']) == record['split'], 'Cross-split graph overlap')
    print(encode_json({'loaded_records': len(records), 'distinct_nonisomeric_graphs': len(graph_splits),
                       'selfies_rechecked': validate_graphs}), flush=True)
    return records, key_map


def audit_spectra():
    templates = load_templates()
    records, key_map = load_records(templates, validate_graphs=True)
    output_path = BASE / 'spectrum_index.jsonl'
    report_path = BASE / 'spectrum_audit_report.json'
    require(not output_path.exists() and not report_path.exists(), 'Spectrum audit output already exists')
    spectrum_types = templates['user_prompt_composition']['spectrum_type_order']
    source_root = Path(templates['input_modes']['spectra']['source_root'])
    references = {record_index: {} for record_index in records}
    unavailable = {record_index: {} for record_index in records}
    report = {'authority_records': len(records), 'files': {}, 'by_type': {}, 'problems': [],
              'policy': 'Use only finite nonempty nonzero source traces. Never zero-fill missing channels.',
              'graph_check': 'Source key canonical nonisomeric graph equals authority target.',
              'physical_recalculation': False}
    for spectrum_type in spectrum_types:
        stats = collections.Counter()
        seen = set()
        required_element = {'xas-c': 'C', 'xas-n': 'N', 'xas-o': 'O',
                            'broad-nmr-h': 'H', 'broad-nmr-c': 'C'}.get(spectrum_type)
        for source_split in ['train', 'test']:
            path = source_root / f'{source_split}_fg26_{spectrum_type}_spectra.parquet'
            source = parquet.ParquetFile(path)
            require(source.schema_arrow.names == ['key', 'dtype', 'shape', 'data'], 'Unknown parquet schema')
            initial_stat = path.stat()
            report['files'][path.name] = {'path': str(path), 'size_bytes': initial_stat.st_size,
                                         'mtime_ns': initial_stat.st_mtime_ns,
                                         'rows': source.metadata.num_rows, 'row_groups': source.num_row_groups}
            absolute_row = 0
            for row_group in range(source.num_row_groups):
                group_row = 0
                for batch in source.iter_batches(batch_size=256, row_groups=[row_group], use_threads=False):
                    columns = batch.to_pydict()
                    for source_key, dtype_text, shape, data in zip(columns['key'], columns['dtype'],
                                                                  columns['shape'], columns['data']):
                        key_id = hashlib.sha256(source_key.encode()).hexdigest()
                        record_index = key_map.get(key_id)
                        locator = {'spectrum_type': spectrum_type, 'source_path': str(path),
                                   'row_group': row_group, 'row_in_group': group_row,
                                   'row_index': absolute_row, 'dtype': dtype_text, 'shape': shape}
                        absolute_row += 1
                        group_row += 1
                        stats['source_rows'] += 1
                        if record_index is None:
                            stats['outside_authority'] += 1
                            continue
                        require(record_index not in seen, f'Duplicate spectrum identity {record_index} {spectrum_type}')
                        seen.add(record_index)
                        record = records[record_index]
                        if spectrum_type == spectrum_types[0]:
                            molecule = Chem.MolFromSmiles(source_key)
                            require(molecule is not None and Chem.MolToSmiles(molecule, canonical=True,
                                    isomericSmiles=False) == record['canonical_smiles'],
                                    f'Parquet source graph mismatch {record_index}')
                        has_element = required_element is None or required_element in record['elements']
                        reason = None
                        if shape == [0] and data == b'':
                            reason = 'absent_element_empty' if not has_element else 'unexpected_empty'
                        elif dtype_text != '<f8' or shape != [4000] or data is None or len(data) != 32000:
                            reason = 'invalid_encoding_or_shape'
                        else:
                            values = np.frombuffer(data, dtype='<f8')
                            if not np.isfinite(values).all():
                                reason = 'nonfinite'
                            elif not np.any(values):
                                reason = 'all_zero'
                            elif not has_element:
                                reason = 'signal_without_required_element'
                            else:
                                locator['data_sha256'] = hashlib.sha256(data).hexdigest()
                                locator['key_id'] = key_id
                                locator['axis_metadata_id'] = spectrum_type
                                references[record_index][spectrum_type] = locator
                                stats['valid'] += 1
                                if np.any(values < 0):
                                    stats['valid_with_negative_values'] += 1
                        if reason:
                            unavailable[record_index][spectrum_type] = reason
                            stats[reason] += 1
                            if reason != 'absent_element_empty' and len(report['problems']) < 100:
                                report['problems'].append({'record_index': record_index,
                                                           'spectrum_type': spectrum_type, 'reason': reason})
                require(group_row == source.metadata.row_group(row_group).num_rows, 'Row-group offset mismatch')
            require(absolute_row == source.metadata.num_rows, 'Parquet row count mismatch')
            require(path.stat().st_size == initial_stat.st_size and path.stat().st_mtime_ns == initial_stat.st_mtime_ns,
                    'Source changed during audit')
            print(encode_json({'audited_file': path.name, 'cumulative_type_counts': dict(stats)}), flush=True)
        for record_index in set(records) - seen:
            unavailable[record_index][spectrum_type] = 'missing_source_row'
            stats['missing_source_row'] += 1
        report['by_type'][spectrum_type] = dict(stats)
    report['valid_spectrum_count_distribution'] = dict(collections.Counter(len(value) for value in references.values()))
    report['available_type_patterns'] = dict(collections.Counter(
        ','.join(spectrum_type for spectrum_type in spectrum_types if spectrum_type in value)
        for value in references.values()))
    temporary = Path(str(output_path) + '.partial')
    with temporary.open('w') as stream:
        for record_index, record in sorted(records.items()):
            stream.write(encode_json({'record_index': record_index, 'key_id': record['key_id'], 'split': record['split'],
                                      'spectra': references[record_index], 'unavailable': unavailable[record_index]}) + '\n')
    temporary.replace(output_path)
    report['spectrum_index_sha256'] = file_sha256(output_path)
    report['source_hashes'] = {field: file_sha256(templates['record_selection'][field])
                               for field in ['authority_path', 'split_path', 'metadata_path']}
    write_json(report_path, report)
    print(encode_json({'spectrum_audit_complete': True,
                       'valid_spectrum_count_distribution': report['valid_spectrum_count_distribution']}), flush=True)


def seeded_rng(*parts):
    digest = hashlib.sha256(encode_json([SEED, *parts]).encode()).digest()
    return random.Random(int.from_bytes(digest[:16], 'big'))


def apportion(total, weights):
    denominator = sum(weights.values())
    allocation = {key: total * weight // denominator for key, weight in weights.items()}
    ranked = sorted(weights, key=lambda key: (-(total * weights[key] % denominator), key))
    for key in ranked[:total - sum(allocation.values())]:
        allocation[key] += 1
    require(sum(allocation.values()) == total, 'Rounding allocation failed')
    return allocation


def join_phrases(phrases):
    if len(phrases) <= 2:
        return ' and '.join(phrases)
    return ', '.join(phrases[:-1]) + ', and ' + phrases[-1]


def formatted_values(record, templates):
    values = {}
    for field, rule in templates['numeric_format'].items():
        if not isinstance(rule, dict):
            continue
        if rule['format'] == 'unchanged':
            values[field] = record[field]
        else:
            values[field] = format(record[field], rule['format'])
            if float(values[field]) == 0:
                values[field] = format(0, rule['format'])
    wording = templates['functional_group_policy']['label_wording']
    values['functional_groups'] = join_phrases([wording[label]['positive_motif_phrase']
                                               for label in record['positive_fg_labels']])
    values['canonical_selfies'] = record['canonical_selfies']
    return values


def load_spectrum_index(records, templates):
    report = json.loads((BASE / 'spectrum_audit_report.json').read_text())
    require(report['spectrum_index_sha256'] == file_sha256(BASE / 'spectrum_index.jsonl'), 'Spectrum index hash changed')
    for field, expected in report['source_hashes'].items():
        require(file_sha256(templates['record_selection'][field]) == expected, 'Audited source hash changed')
    for source in report['files'].values():
        stat = Path(source['path']).stat()
        require(stat.st_size == source['size_bytes'] and stat.st_mtime_ns == source['mtime_ns'],
                f'Spectrum source changed {source["path"]}')
    index = {}
    with (BASE / 'spectrum_index.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line)
            record_index = row['record_index']
            require(record_index in records and record_index not in index, 'Invalid spectrum index identity')
            require(row['key_id'] == records[record_index]['key_id'] and row['split'] == records[record_index]['split'],
                    'Spectrum index join mismatch')
            require(bool(row['spectra']), f'No valid spectra for record {record_index}')
            for spectrum_type, reference in row['spectra'].items():
                require(reference['key_id'] == row['key_id'] and reference['spectrum_type'] == spectrum_type,
                        'Spectrum reference identity mismatch')
                require(reference['shape'] == [4000] and reference['dtype'] == '<f8', 'Invalid audited encoding')
            index[record_index] = row['spectra']
    require(set(index) == set(records), 'Spectrum index membership mismatch')
    return index


def choose_records(record_ids, total, tag):
    require(total <= len(record_ids), f'Not enough eligible records for {tag}')
    return seeded_rng('record_selection', *tag).sample(sorted(record_ids), total)


def allocate_spectrum_subsets(record_ids, copies, spectrum_index, templates, tag):
    order = templates['user_prompt_composition']['spectrum_type_order']
    weights = {int(key): value for key, value in
               templates['user_prompt_composition']['subset_sampling']['count_weights_percent'].items()}
    quotas = apportion(len(record_ids) * copies, weights)
    rng = seeded_rng('spectrum_subsets', *tag)
    available = {record_index: tuple(spectrum_type for spectrum_type in order
                                     if spectrum_type in spectrum_index[record_index]) for record_index in record_ids}
    remaining = {record_index: copies for record_index in record_ids}
    used = collections.defaultdict(set)
    result = []
    for minimum in range(1, 9):
        capacity = sum(min(copies, sum(math.comb(len(types), count)
                       for count in range(minimum, len(types) + 1))) for types in available.values())
        demand = sum(quotas[count] for count in range(minimum, 9))
        require(capacity >= demand, f'Infeasible spectrum quotas {tag}, minimum cardinality {minimum}')
    for spectrum_count in range(8, 0, -1):
        eligible_slots = []
        for record_index, types in available.items():
            if len(types) < spectrum_count or not remaining[record_index]:
                continue
            capacity = min(remaining[record_index], math.comb(len(types), spectrum_count))
            eligible_slots.extend([record_index] * capacity)
        require(len(eligible_slots) >= quotas[spectrum_count], f'Insufficient slots for {tag}, {spectrum_count}')
        rng.shuffle(eligible_slots)
        for record_index in eligible_slots[:quotas[spectrum_count]]:
            choices = [combination for combination in itertools.combinations(available[record_index], spectrum_count)
                       if combination not in used[record_index]]
            require(bool(choices), 'Repeated spectral subset has exhausted choices')
            selected = rng.choice(choices)
            variant = copies - remaining[record_index]
            result.append((record_index, variant, selected))
            remaining[record_index] -= 1
            used[record_index].add(selected)
    require(all(value == 0 for value in remaining.values()), f'Unfilled spectrum examples {tag}')
    actual = collections.Counter(len(entry[2]) for entry in result)
    require(all(actual[size] == count for size, count in quotas.items()), 'Realized spectrum quota mismatch')
    return result, quotas


class BalancedPicker:
    def __init__(self):
        self.states = {}

    def choose(self, key, size):
        key = tuple(key)
        if key not in self.states:
            self.states[key] = {'rng': seeded_rng('template', *key), 'deck': [], 'counts': [0] * size}
        state = self.states[key]
        require(len(state['counts']) == size, f'Changing compatible template pool {key}')
        if not state['deck']:
            state['deck'] = list(range(size))
            state['rng'].shuffle(state['deck'])
        position = state['deck'].pop()
        state['counts'][position] += 1
        return position

    def report(self):
        output = {}
        for key, state in self.states.items():
            counts = state['counts']
            require(max(counts) - min(counts) <= 1, f'Unbalanced template pool {key}')
            output['|'.join(map(str, key))] = counts
        return output


def build_recipes(records, spectrum_index, templates):
    targets = templates['corpus_recipe']['per_task_mode_counts']
    weights = templates['record_selection']['split_counts']
    split_ids = {split: [record_index for record_index, record in records.items() if record['split'] == split]
                 for split in weights}
    selections = {}
    scalar_val_counts = apportion(weights['val'], {task: 1 for task in SCALAR_TASKS})
    for split, record_ids in split_ids.items():
        shuffled = sorted(record_ids)
        seeded_rng('scalar_partition', split).shuffle(shuffled)
        offset = 0
        for task in SCALAR_TASKS:
            count = scalar_val_counts[task] if split == 'val' else targets[task]['structure_3d'] - scalar_val_counts[task]
            selections[(split, 'structure_3d', task)] = shuffled[offset:offset + count]
            offset += count
        require(offset == len(record_ids), 'Scalar partition does not cover records exactly once')
        for task, mode_targets in targets.items():
            if task in SCALAR_TASKS:
                continue
            if task == 'selfies_nonisomeric':
                for mode in ['structure_3d', 'spectra']:
                    selections[(split, mode, task)] = sorted(record_ids)
            elif task in ['formula', FG_TASK]:
                eligible = [record_index for record_index in record_ids
                            if task != FG_TASK or records[record_index]['positive_fg_labels']]
                count = apportion(mode_targets['structure_3d'], weights)[split]
                selected = choose_records(eligible, count, (split, task))
                for mode in ['structure_3d', 'spectra']:
                    selections[(split, mode, task)] = selected
            else:
                for mode, total in mode_targets.items():
                    count = apportion(total, weights)[split]
                    selections[(split, mode, task)] = choose_records(record_ids, count, (split, mode, task))
    recipes = {split: [] for split in weights}
    spectrum_quotas = {}
    for (split, mode, task), record_ids in sorted(selections.items()):
        if mode == 'spectra':
            copies = 2 if task == 'selfies_nonisomeric' else 1
            selected_inputs, quotas = allocate_spectrum_subsets(record_ids, copies, spectrum_index, templates,
                                                               (split, mode, task))
            spectrum_quotas['|'.join([split, mode, task])] = quotas
        else:
            selected_inputs = [(record_index, 0, ()) for record_index in record_ids]
        recipes[split].extend((record_index, mode, task, variant, subset)
                              for record_index, variant, subset in selected_inputs)
    actual = collections.Counter((mode, task) for values in recipes.values()
                                 for record_index, mode, task, variant, subset in values)
    for task, mode_targets in targets.items():
        for mode, count in mode_targets.items():
            require(actual[(mode, task)] == count, f'Planned task count mismatch {mode} {task}')
    for split, values in recipes.items():
        seeded_rng('final_order', split).shuffle(values)
    return recipes, spectrum_quotas


def render_example(record, mode, task, variant, subset, templates, spectrum_index, picker):
    group = next(group for group in templates['groups'] if group['id'] == task)
    require(mode in group['input_modes'], 'Task input mode is disabled')
    values = formatted_values(record, templates)
    subgroup = str(record['aromatic']) if task == 'aromatic_presence' else 'all'
    balance_key = (record['split'], mode, task, subgroup)
    query_index = picker.choose((*balance_key, 'query'), len(group['queries']))
    preamble_pool = 'structure_3d' if mode == 'structure_3d' else 'single_spectrum' if len(subset) == 1 else 'multiple_spectra'
    composition = templates['user_prompt_composition']
    preambles = composition['templates'][preamble_pool]
    preamble_index = picker.choose((*balance_key, 'preamble', preamble_pool), len(preambles))
    names = [composition['spectrum_type_names'][spectrum_type] for spectrum_type in subset]
    preamble = preambles[preamble_index].format(spectrum_name=names[0] if names else '',
                                               spectrum_names=join_phrases(names))
    output = {'sample_id': f'fg26_{record["record_index"]}_{mode}_{task}_{variant}',
              'record_index': record['record_index'], 'key_id': record['key_id'], 'split': record['split'],
              'task': task, 'input_mode': mode, 'variant': variant,
              'query_template_id': f'{task}.q{query_index + 1:02d}',
              'input_preamble_template_id': f'{preamble_pool}.p{preamble_index + 1:02d}'}
    if task == 'factual_description':
        compatible = [scheme for scheme in group['combination_schemes'] if mode in scheme['input_modes']
                      and ('functional_groups' not in scheme['modules'] or record['positive_fg_labels'])]
        scheme_index = picker.choose((*balance_key, 'scheme', bool(record['positive_fg_labels'])), len(compatible))
        scheme = compatible[scheme_index]
        module_ids = []
        sentences = []
        for field in scheme['modules']:
            module = group['description_modules'][field]
            module_subgroup = str(record['aromatic']) if field == 'aromatic' else 'all'
            if field == 'aromatic':
                module = module['responses_positive' if record['aromatic'] else 'responses_negative']
            wording_index = picker.choose((*balance_key, 'module', field, module_subgroup), len(module))
            sentences.append(module[wording_index].format(**values))
            module_ids.append({'module': field, 'subgroup': module_subgroup, 'template_index': wording_index})
        values['description'] = ' '.join(sentences)
        output['description_combination_id'] = scheme['combination_id']
        output['description_module_templates'] = module_ids
        output['target_fields'] = scheme['modules']
    else:
        output['target_fields'] = ['functional_groups'] if task == FG_TASK else group['source_fields']
    response_pool = 'responses'
    if task == 'aromatic_presence':
        response_pool = 'responses_positive' if record['aromatic'] else 'responses_negative'
    response_index = picker.choose((*balance_key, response_pool), len(group[response_pool]))
    output['response_template_id'] = f'{task}.{response_pool}.r{response_index + 1:02d}'
    output['messages'] = [{'role': 'user', 'content': preamble + ' ' + group['queries'][query_index]},
                          {'role': 'assistant', 'content': group[response_pool][response_index].format(**values)}]
    if mode == 'structure_3d':
        for field in ['input_xyz_path', 'input_xyz_relative_path', 'input_xyz_sha256']:
            output[field] = record[field]
    else:
        output['spectrum_types'] = list(subset)
        output['input_spectrum_refs'] = [spectrum_index[record['record_index']][spectrum_type] for spectrum_type in subset]
    if any(field in output['target_fields'] for field in ['homo_eV', 'lumo_eV', 'dipole_debye', 'polarizability_au']):
        output['calculation'] = record['calculation']
    if 'functional_groups' in output['target_fields']:
        output['selected_fg_labels'] = record['positive_fg_labels']
    if task == 'selfies_nonisomeric':
        output['selfies_policy'] = record['selfies_policy']
    return output


def validate_example(example, record, templates, spectrum_index):
    group = next(group for group in templates['groups'] if group['id'] == example['task'])
    mode = example['input_mode']
    require(mode in group['input_modes'], 'Disabled modality')
    require(example['record_index'] == record['record_index'] and example['key_id'] == record['key_id']
            and example['split'] == record['split'], 'Corpus target identity mismatch')
    require(example['sample_id'] == f'fg26_{record["record_index"]}_{mode}_{group["id"]}_{example["variant"]}',
            'Sample ID does not match its record or task')
    require([message['role'] for message in example['messages']] == ['user', 'assistant'], 'Invalid roles')
    for message in example['messages']:
        content = message['content']
        require(content and content == content.strip() and not FORBIDDEN.search(content), 'Forbidden message text')
    require('system' not in example and 'canonical_smiles' not in example and 'canonical_selfies' not in example,
            'Unneeded source target strings in conversation record')
    composition = templates['user_prompt_composition']
    preamble_pool, preamble_id = example['input_preamble_template_id'].rsplit('.p', 1)
    if mode == 'structure_3d':
        require('input_spectrum_refs' not in example and 'spectrum_types' not in example, 'Mixed input modes')
        require(preamble_pool == 'structure_3d', 'Wrong premise group')
        for field in ['input_xyz_path', 'input_xyz_relative_path', 'input_xyz_sha256']:
            require(example[field] == record[field], 'Wrong XYZ reference')
        names = []
    else:
        require('input_xyz_path' not in example, 'Mixed input modes')
        types = example['spectrum_types']
        require(1 <= len(types) <= 8 and len(types) == len(set(types)), 'Invalid subset size or duplicate type')
        require(types == [value for value in composition['spectrum_type_order'] if value in types], 'Wrong spectrum order')
        require(preamble_pool == ('single_spectrum' if len(types) == 1 else 'multiple_spectra'), 'Wrong plural premise')
        expected = [spectrum_index[record['record_index']][value] for value in types]
        require(example['input_spectrum_refs'] == expected, 'Wrong spectral source reference')
        require(not set(example['target_fields']) - {'formula', 'functional_groups', 'aromatic', 'canonical_selfies'},
                'Scalar label in spectrum target')
        names = [composition['spectrum_type_names'][value] for value in types]
    preamble = composition['templates'][preamble_pool][int(preamble_id) - 1].format(
        spectrum_name=names[0] if names else '', spectrum_names=join_phrases(names))
    query_group, query_id = example['query_template_id'].rsplit('.q', 1)
    require(query_group == group['id'], 'Wrong query group')
    require(example['messages'][0]['content'] == preamble + ' ' + group['queries'][int(query_id) - 1],
            'Query does not match actual inputs and template')
    values = formatted_values(record, templates)
    if group['id'] == 'factual_description':
        scheme = next(scheme for scheme in group['combination_schemes']
                      if scheme['combination_id'] == example['description_combination_id'])
        require(mode in scheme['input_modes'], 'Disabled description mode')
        require(example['target_fields'] == scheme['modules'], 'Description target mismatch')
        require([entry['module'] for entry in example['description_module_templates']] == scheme['modules'],
                'Description order mismatch')
        sentences = []
        for entry in example['description_module_templates']:
            module = group['description_modules'][entry['module']]
            if entry['module'] == 'aromatic':
                require(entry['subgroup'] == str(record['aromatic']), 'Wrong aromatic module branch')
                module = module['responses_positive' if record['aromatic'] else 'responses_negative']
            else:
                require(entry['subgroup'] == 'all', 'Wrong module subgroup')
            sentences.append(module[entry['template_index']].format(**values))
        values['description'] = ' '.join(sentences)
    else:
        expected_fields = ['functional_groups'] if group['id'] == FG_TASK else group['source_fields']
        require(example['target_fields'] == expected_fields, 'Wrong direct target fields')
    response_group, response_pool, response_id = example['response_template_id'].rsplit('.', 2)
    require(response_group == group['id'], 'Wrong response group')
    expected_pool = ('responses_positive' if record['aromatic'] else 'responses_negative') \
        if group['id'] == 'aromatic_presence' else 'responses'
    require(response_pool == expected_pool, 'Wrong response label branch')
    require(example['messages'][1]['content'] == group[response_pool][int(response_id[1:]) - 1].format(**values),
            'Response differs from source labels or compatible template')
    if 'functional_groups' in example['target_fields']:
        require(record['positive_fg_labels'] and example['selected_fg_labels'] == record['positive_fg_labels'],
                'Empty or wrong positive FG answer')
    if group['id'] == 'selfies_nonisomeric':
        require(example['messages'][1]['content'] == record['canonical_selfies'], 'SELFIES altered')
        require(example['selfies_policy'] == record['selfies_policy'], 'Wrong SELFIES policy')
    scalar_fields = {'homo_eV', 'lumo_eV', 'dipole_debye', 'polarizability_au'}
    if set(example['target_fields']) & scalar_fields:
        require(example['calculation'] == record['calculation'], 'Wrong calculation provenance')
    return True


def validate_templates(templates):
    require(templates['schema_version'] == 4, 'Unexpected template schema')
    groups = templates['groups']
    require(len(groups) == 9, 'Wrong task count')
    formatter = Formatter()
    checked = 0
    for group in groups:
        require(len(group['queries']) == len(set(group['queries'])) == 16, 'Query expansion count mismatch')
        require(group['input_modes'] == (['structure_3d'] if group['id'] in SCALAR_TASKS else ['spectra', 'structure_3d']),
                'Wrong task routing')
        strings = list(group['queries'])
        for field in ['responses', 'responses_positive', 'responses_negative']:
            if field in group:
                require(len(group[field]) == len(set(group[field])), 'Duplicate response templates')
                strings.extend(group[field])
        if group['id'] == 'factual_description':
            for module in group['description_modules'].values():
                strings.extend(module if isinstance(module, list) else module['responses_positive'] + module['responses_negative'])
            for scheme in group['combination_schemes']:
                require(len(scheme['modules']) == len(set(scheme['modules'])) >= 2, 'Invalid description scheme')
                if 'spectra' in scheme['input_modes']:
                    require(set(scheme['modules']) <= {'formula', 'aromatic', 'functional_groups'}, 'Scalar spectral description')
        for message in strings:
            fields = {field for text, field, spec, conversion in formatter.parse(message) if field is not None}
            rendered = message.format(**{field: 'VALIDATEDVALUE' for field in fields})
            require(not FORBIDDEN.search(rendered), f'Forbidden template text {message}')
            require(not fields or message not in group['queries'], 'Unexpected slot in core query')
            checked += 1
    composition = templates['user_prompt_composition']
    for pool_name, pool in composition['templates'].items():
        require(len(pool) == len(set(pool)) == 20, 'Premise expansion count mismatch')
        require(sum('provided' in sentence.lower() for sentence in pool) == 1, 'Passive provided not diversified')
        expected_fields = set() if pool_name == 'structure_3d' else {'spectrum_name'} if pool_name == 'single_spectrum' else {'spectrum_names'}
        for sentence in pool:
            fields = {field for text, field, spec, conversion in formatter.parse(sentence) if field is not None}
            require(fields == expected_fields, 'Wrong premise slots')
    for size in range(1, 9):
        for subset in itertools.combinations(composition['spectrum_type_order'], size):
            names = [composition['spectrum_type_names'][value] for value in subset]
            pool = composition['templates']['single_spectrum' if size == 1 else 'multiple_spectra']
            for sentence in pool:
                preamble = sentence.format(spectrum_name=names[0], spectrum_names=join_phrases(names))
                for group in groups:
                    if 'spectra' not in group['input_modes']:
                        continue
                    for query in group['queries']:
                        require(not FORBIDDEN.search(preamble + ' ' + query), 'Invalid composed spectrum query')
                        checked += 1
    for preamble in composition['templates']['structure_3d']:
        for group in groups:
            for query in group['queries']:
                require(not FORBIDDEN.search(preamble + ' ' + query), 'Invalid structure query')
                checked += 1
    return {'template_and_complete_prompt_checks': checked, 'counts': templates['counts']}


def generate_corpus():
    templates = load_templates()
    template_validation = validate_templates(templates)
    require(not any((BASE / name).exists() for name in ['train.jsonl', 'val.jsonl', 'preview.jsonl', 'corpus_report.json']),
            'Corpus output already exists; refusing overwrite')
    records, key_map = load_records(templates, validate_graphs=False)
    spectrum_index = load_spectrum_index(records, templates)
    recipes, quotas = build_recipes(records, spectrum_index, templates)
    print(encode_json({'planned_split_counts': {split: len(values) for split, values in recipes.items()}}), flush=True)
    picker = BalancedPicker()
    counts = collections.Counter()
    spectrum_counts = collections.defaultdict(collections.Counter)
    type_counts = collections.defaultdict(collections.Counter)
    fg_counts = collections.defaultdict(collections.Counter)
    preview_counts = collections.Counter()
    preview = []
    for split, planned in recipes.items():
        temporary = BASE / f'{split}.jsonl.partial'
        with temporary.open('w', buffering=8 * 1024 * 1024) as stream:
            for position, (record_index, mode, task, variant, subset) in enumerate(planned):
                example = render_example(records[record_index], mode, task, variant, subset, templates, spectrum_index, picker)
                validate_example(example, records[record_index], templates, spectrum_index)
                stream.write(encode_json(example) + '\n')
                key = '|'.join([split, mode, task])
                counts[key] += 1
                if mode == 'spectra':
                    spectrum_counts[key][len(subset)] += 1
                    type_counts[key].update(subset)
                if 'selected_fg_labels' in example:
                    fg_counts[key].update(example['selected_fg_labels'])
                if preview_counts[key] < 5:
                    preview.append(example)
                    preview_counts[key] += 1
                if (position + 1) % 100000 == 0:
                    print(encode_json({'generated_split': split, 'rows': position + 1}), flush=True)
    require(sum(counts.values()) == templates['corpus_recipe']['target_total'], 'Total generated count mismatch')
    for key, expected in quotas.items():
        require(dict(spectrum_counts[key]) == expected, 'Actual spectral count distribution mismatch')
    balance = picker.report()
    with (BASE / 'preview.jsonl.partial').open('w') as stream:
        for example in sorted(preview, key=lambda value: (value['split'], value['input_mode'], value['task'], value['sample_id'])):
            stream.write(encode_json(example) + '\n')
    report = {'status': 'generated_pending_independent_readback', 'total': sum(counts.values()),
              'split_counts': {split: len(values) for split, values in recipes.items()}, 'by_split_mode_task': dict(counts),
              'spectrum_count_quotas': quotas, 'spectrum_count_actual': dict(spectrum_counts),
              'spectrum_type_counts': dict(type_counts), 'positive_fg_label_counts': dict(fg_counts),
              'template_usage_by_compatible_pool': balance, 'template_validation': template_validation,
              'preview_rows': len(preview), 'seed': SEED, 'template_sha256': file_sha256(TEMPLATE_PATH),
              'generator_sha256': file_sha256(Path(__file__)),
              'spectrum_index_sha256': file_sha256(BASE / 'spectrum_index.jsonl'),
              'record_count': len(records), 'source_split_counts': templates['record_selection']['split_counts'],
              'full_xyz_bond_order_reconstruction': False,
              'audit_boundary': 'Exact source binding and label rendering, not inverse uniqueness or rerun quantum calculations.'}
    write_json(BASE / 'corpus_report.json', report)
    print(encode_json({'generation_complete_pending_readback': True, 'total': report['total']}), flush=True)


def reread_spectral_sources(spectrum_index):
    chosen = collections.defaultdict(list)
    seen = collections.Counter()
    rng = seeded_rng('spectral_source_readback')
    for references in spectrum_index.values():
        for reference in references.values():
            path = reference['source_path']
            seen[path] += 1
            if len(chosen[path]) < 4:
                chosen[path].append(reference)
            else:
                position = rng.randrange(seen[path])
                if position < 4:
                    chosen[path][position] = reference
    verified = 0
    for path, references in sorted(chosen.items()):
        source = parquet.ParquetFile(path)
        groups = collections.defaultdict(dict)
        for reference in references:
            groups[reference['row_group']][reference['row_in_group']] = reference
        for row_group, requested in groups.items():
            offset = sum(source.metadata.row_group(position).num_rows for position in range(row_group))
            group_row = 0
            for batch in source.iter_batches(batch_size=256, row_groups=[row_group], use_threads=False):
                columns = batch.to_pydict()
                for source_key, dtype_text, shape, data in zip(columns['key'], columns['dtype'], columns['shape'], columns['data']):
                    reference = requested.get(group_row)
                    if reference is not None:
                        require(reference['row_index'] == offset + group_row, 'Wrong absolute spectral row locator')
                        require(hashlib.sha256(source_key.encode()).hexdigest() == reference['key_id'], 'Spectral key readback mismatch')
                        require(hashlib.sha256(data).hexdigest() == reference['data_sha256'], 'Spectral data readback mismatch')
                        require(dtype_text == reference['dtype'] and shape == reference['shape'], 'Spectral encoding readback mismatch')
                        array = np.frombuffer(data, dtype=dtype_text)
                        require(array.size == 4000 and np.isfinite(array).all() and np.any(array), 'Invalid reread spectral input')
                        verified += 1
                    group_row += 1
                if group_row > max(requested):
                    break
        print(encode_json({'spectral_source_readback_file': Path(path).name, 'verified_cumulative': verified}), flush=True)
    require(verified == sum(len(values) for values in chosen.values()), 'Incomplete spectral source readback')
    return {'references': verified, 'source_files': len(chosen)}


def verify_corpus():
    templates = load_templates()
    report = json.loads((BASE / 'corpus_report.json').read_text())
    require(report['template_sha256'] == file_sha256(TEMPLATE_PATH), 'Templates changed after generation')
    records, key_map = load_records(templates, validate_graphs=False)
    spectrum_index = load_spectrum_index(records, templates)
    counts = collections.Counter()
    record_tasks = collections.Counter()
    spectral_duplicates = set()
    sample_ids = set()
    spectrum_counts = collections.defaultdict(collections.Counter)
    selected_records = collections.defaultdict(set)
    hashes = {}
    total = 0
    preview_path = BASE / 'preview.jsonl.partial'
    if not preview_path.exists():
        preview_path = BASE / 'preview.jsonl'
    with preview_path.open() as stream:
        preview = [json.loads(line) for line in stream]
    require(len(preview) == report['preview_rows'], 'Preview count mismatch')
    preview_by_id = {example['sample_id']: example for example in preview}
    require(len(preview_by_id) == len(preview), 'Duplicate preview sample ID')
    matched_preview = set()
    for split in ['train', 'val']:
        pending = BASE / f'{split}.jsonl.partial'
        path = pending if pending.exists() else BASE / f'{split}.jsonl'
        with path.open() as stream:
            for line in stream:
                example = json.loads(line)
                require(example['split'] == split, 'Wrong output split')
                record = records[example['record_index']]
                validate_example(example, record, templates, spectrum_index)
                require(example['sample_id'] not in sample_ids, 'Duplicate sample ID')
                sample_ids.add(example['sample_id'])
                if example['sample_id'] in preview_by_id:
                    require(example == preview_by_id[example['sample_id']], 'Preview differs from its actual corpus row')
                    matched_preview.add(example['sample_id'])
                mode, task = example['input_mode'], example['task']
                key = '|'.join([split, mode, task])
                counts[key] += 1
                record_tasks[(record['record_index'], mode, task)] += 1
                selected_records[(mode, task)].add(record['record_index'])
                if mode == 'spectra':
                    subset = tuple(example['spectrum_types'])
                    duplicate_key = (record['record_index'], task, subset)
                    require(duplicate_key not in spectral_duplicates, 'Repeated record/task/spectrum combination')
                    spectral_duplicates.add(duplicate_key)
                    spectrum_counts[key][len(subset)] += 1
                total += 1
                if total % 200000 == 0:
                    print(encode_json({'readback_verified': total}), flush=True)
        hashes[f'{split}.jsonl'] = file_sha256(path)
    require(dict(counts) == report['by_split_mode_task'] and total == report['total'], 'Readback counts mismatch')
    for key, expected in report['spectrum_count_quotas'].items():
        require(dict(spectrum_counts[key]) == {int(size): count for size, count in expected.items()},
                'Readback spectral quotas mismatch')
    for (record_index, mode, task), count in record_tasks.items():
        require(count == (2 if mode == 'spectra' and task == 'selfies_nonisomeric' else 1), 'Wrong per-record task repeats')
    for record_index in records:
        require(record_tasks[(record_index, 'structure_3d', 'selfies_nonisomeric')] == 1 and
                record_tasks[(record_index, 'spectra', 'selfies_nonisomeric')] == 2, 'SELFIES record coverage mismatch')
        require(sum(record_tasks[(record_index, 'structure_3d', task)] for task in SCALAR_TASKS) == 1,
                'Scalar partition coverage mismatch')
    for task in ['formula', FG_TASK]:
        require(selected_records[('structure_3d', task)] == selected_records[('spectra', task)] and
                len(selected_records[('structure_3d', task)]) == 116974, 'Half-record task coverage mismatch')
    xyz_names = set()
    for prefix in os.scandir(BASE / 'structures'):
        if prefix.is_dir():
            xyz_names.update(Path(entry.path).relative_to(BASE).as_posix()
                             for entry in os.scandir(prefix.path) if entry.is_file() and entry.name.endswith('.xyz'))
    require(xyz_names == {record['input_xyz_relative_path'] for record in records.values()}, 'XYZ file inventory mismatch')
    xyz_sample = seeded_rng('xyz_readback').sample(sorted(records), 64)
    for record_index in xyz_sample:
        record = records[record_index]
        path = Path(record['input_xyz_path'])
        require(file_sha256(path) == record['input_xyz_sha256'], 'XYZ changed since export')
        lines = path.read_text().splitlines()
        require(int(lines[0]) == record['n_atoms'] and not lines[1] and len(lines) == record['n_atoms'] + 2,
                'XYZ content or comment mismatch')
        coordinates = np.array([[float(value) for value in line.split()[1:]] for line in lines[2:]])
        require(coordinates.shape == (record['n_atoms'], 3) and np.isfinite(coordinates).all(), 'Invalid XYZ coordinates')
    require(matched_preview == set(preview_by_id), 'Preview row missing from actual corpus')
    for example in preview:
        require(example['sample_id'] in sample_ids, 'Preview not from generated corpus')
        validate_example(example, records[example['record_index']], templates, spectrum_index)
    spectral_readback = reread_spectral_sources(spectrum_index)
    hashes['preview.jsonl'] = file_sha256(preview_path)
    for name in ['train.jsonl', 'val.jsonl', 'preview.jsonl']:
        pending = BASE / (name + '.partial')
        if pending.exists():
            require(not (BASE / name).exists(), f'Refusing to replace {name}')
            pending.replace(BASE / name)
    report['status'] = 'accepted_full_conversation_readback'
    report['output_sha256'] = hashes
    report['verification_script_sha256'] = file_sha256(Path(__file__))
    report['source_hashes_verified'] = templates['source_sha256']
    report['readback_validation'] = {'messages_and_labels_checked': total, 'duplicate_sample_ids': 0,
                                    'duplicate_spectrum_subsets_within_record_task': 0,
                                    'cross_split_stored_nonisomeric_graph_overlap': 0,
                                    'xyz_files_present': len(xyz_names), 'xyz_hash_readback_sample': len(xyz_sample),
                                    'preview_verified_rows': len(preview), 'spectral_source_readback': spectral_readback}
    write_json(BASE / 'corpus_report.json', report)
    print(encode_json({'accepted': True, 'total': total, 'split_counts': report['split_counts']}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['audit', 'templates', 'generate', 'verify'])
    arguments = parser.parse_args()
    if arguments.stage == 'audit':
        audit_spectra()
    elif arguments.stage == 'templates':
        print(encode_json(validate_templates(load_templates())))
    elif arguments.stage == 'generate':
        generate_corpus()
    elif arguments.stage == 'verify':
        verify_corpus()


if __name__ == '__main__':
    main()
