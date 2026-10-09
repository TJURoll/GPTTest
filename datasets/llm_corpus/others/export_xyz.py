import csv
import hashlib
import json
import math
import re
import shlex
import tarfile
import time
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from rdkit import Chem


ROOT = Path('/mnt/e/Datasets/fg26')
OUTPUT = Path(__file__).resolve().parent
AUTHORITY = ROOT / '04_training_data/repository_data/phase15_aux/canonical_selfies_by_record_index_v17_nonisomeric.jsonl'
SPLITS = ROOT / '04_training_data/repository_data/split_maps/phase2_v26_record_split_map.jsonl'
METADATA = ROOT / '01_source_data/metadata/molecule_tables/fg26_molecule_metadata_v2_corrected_units.csv'
CACHE = ROOT / '03_feature_caches/structures/fg26_structure_npz/structures_clean_muse_v1'
ARCHIVE = ROOT / '01_source_data/parsed_exact/parsed_exact_v1_234554.tar'
SCALARS = {
    'scf_energy_eV': ('scf_energy_eV', 'scf', 'energy_eV', np.float64),
    'homo_eV': ('homo_eV', 'orbital_energies', 'homo_eV', np.float32),
    'lumo_eV': ('lumo_eV', 'orbital_energies', 'lumo_eV', np.float32),
    'gap_eV': ('gap_eV', 'orbital_energies', 'gap_eV', np.float32),
    'dipole_debye': ('dipole_debye', 'dipole', 'total_debye', np.float32),
    'polarizability_au': ('polarizability_isotropic', 'polarizability', 'isotropic', np.float32),
}
PERIODIC_TABLE = Chem.GetPeriodicTable()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_line(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n'


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def stamp(path):
    status = path.stat()
    return {'size': status.st_size, 'mtime_ns': status.st_mtime_ns}


def geometry_hash(atomic_numbers, positions):
    numbers = np.asarray(atomic_numbers, dtype='<i2')
    coordinates = np.asarray(positions, dtype='<f4').copy()
    coordinates[coordinates == 0] = 0
    return hashlib.sha256(numbers.tobytes() + coordinates.tobytes()).hexdigest()


def parse_xyz(payload):
    lines = payload.decode('utf-8').splitlines()
    atom_count = int(lines[0])
    require(atom_count > 0 and len(lines) >= atom_count + 2, 'Invalid XYZ atom count')
    require(not any(line.strip() for line in lines[atom_count + 2:]), 'Unexpected XYZ trailing content')
    body = [line.split() for line in lines[2:atom_count + 2]]
    require(all(len(fields) == 4 for fields in body), 'Unexpected XYZ atom columns')
    numbers = np.array([PERIODIC_TABLE.GetAtomicNumber(fields[0]) for fields in body], dtype=np.int16)
    coordinates = np.array([[float(value) for value in fields[1:]] for fields in body], dtype=np.float64)
    require(bool(np.all(numbers > 0) and np.isfinite(coordinates).all()), 'Invalid XYZ atoms or coordinates')
    return lines, numbers, coordinates


def write_and_check(path, payload, expected_numbers, expected_coordinates):
    with path.open('xb') as handle:
        handle.write(payload)
    readback = path.read_bytes()
    require(readback == payload, f'XYZ byte roundtrip failure {path}')
    lines, numbers, coordinates = parse_xyz(readback)
    require(lines[1] == '', f'XYZ comment contains metadata {path}')
    require(np.array_equal(numbers, expected_numbers), f'XYZ atom roundtrip failure {path}')
    require(np.array_equal(coordinates, expected_coordinates), f'XYZ coordinate roundtrip failure {path}')
    return hashlib.sha256(readback).hexdigest()


class HashingReader:
    def __init__(self, handle):
        self.handle = handle
        self.digest = hashlib.sha256()

    def read(self, size=-1):
        payload = self.handle.read(size)
        self.digest.update(payload)
        return payload


def main():
    started = time.monotonic()
    pending_structures = OUTPUT / 'structures.pending'
    final_structures = OUTPUT / 'structures'
    pending_index = OUTPUT / 'structure_index.pending.jsonl'
    final_index = OUTPUT / 'structure_index.jsonl'
    report_path = OUTPUT / 'xyz_export_report.json'
    require(not any(path.exists() for path in [pending_structures, final_structures, pending_index, final_index, report_path]), 'Output already exists; refusing to overwrite')
    source_paths = [AUTHORITY, SPLITS, METADATA, ARCHIVE, CACHE / 'manifest.json']
    snapshots = {str(path): stamp(path) for path in source_paths}
    source_hashes = {str(path): file_hash(path) for path in source_paths if path != ARCHIVE}
    authority = {}
    representation_splits = {}
    with AUTHORITY.open() as handle:
        for line in handle:
            record = json.loads(line)
            record_index = int(record['record_index'])
            require(record_index not in authority, f'Duplicate authority record {record_index}')
            authority[record_index] = record
    splits = {}
    with SPLITS.open() as handle:
        for line in handle:
            record = json.loads(line)
            record_index = int(record['record_index'])
            require(record_index not in splits, f'Duplicate split record {record_index}')
            require(record['split'] in ('train', 'val'), 'Unknown split')
            splits[record_index] = record['split']
    require(authority.keys() == splits.keys(), 'Authority and split membership differ')
    for record_index, record in authority.items():
        representation_splits.setdefault(record['canonical_smiles'], set()).add(splits[record_index])
    require(all(len(values) == 1 for values in representation_splits.values()), 'Stored nonisomeric SMILES overlap train and val')
    records = {}
    by_key = {}
    metadata_ids = set()
    extra_metadata = []
    scalar_counts = Counter()
    flag_counts = Counter()
    old_split_disagreements = 0
    max_gap_residual = 0.0
    max_polarizability_residual = 0.0
    with METADATA.open(newline='') as handle:
        reader = csv.DictReader(handle)
        flag_fields = [field for field in reader.fieldnames if field.startswith('fg_')] + ['aromatic', 'aromatic_phase2_label']
        for row in reader:
            record_index = int(row['record_index'])
            require(record_index not in metadata_ids, f'Duplicate metadata record {record_index}')
            metadata_ids.add(record_index)
            if record_index not in authority:
                extra_metadata.append(record_index)
                continue
            key_id = row['key_id']
            require(re.fullmatch('[0-9a-f]{64}', key_id) is not None, 'Invalid key_id')
            require(key_id not in by_key, f'Duplicate authority key_id {key_id}')
            require(row['canonical_smiles'] == authority[record_index]['canonical_smiles_isomeric'], f'SMILES authority mismatch {record_index}')
            old_split_disagreements += row['split'] != splits[record_index]
            values = {field: float(row[field]) for field in [*SCALARS, 'polarizability_A3']}
            for field, value in values.items():
                require(math.isfinite(value), f'Nonfinite metadata {record_index} {field}')
                scalar_counts[field] += 1
            for field in flag_fields:
                require(row[field] in ('0', '1'), f'Invalid annotation {record_index} {field}')
                flag_counts[field] += 1
            max_gap_residual = max(max_gap_residual, abs(values['gap_eV'] - (values['lumo_eV'] - values['homo_eV'])))
            max_polarizability_residual = max(max_polarizability_residual, abs(values['polarizability_A3'] - values['polarizability_au'] * 0.14818471147216278))
            records[record_index] = {
                'record_index': record_index,
                'key_id': key_id,
                'split': splits[record_index],
                'formula': row['formula'],
                'n_atoms': int(row['n_atoms']),
                'values': values,
            }
            by_key[key_id] = records[record_index]
    require(records.keys() == authority.keys(), 'Missing metadata for authority records')
    del authority
    print(json_line({'stage': 'metadata_checked', 'records': len(records), 'split': dict(Counter(splits.values()))}), end='', flush=True)
    manifest = json.loads((CACHE / 'manifest.json').read_text())
    cache_seen = set()
    extra_cache = []
    cache_scalar_counts = Counter()
    for shard_info in manifest['shards']:
        shard_path = CACHE / shard_info['path']
        snapshots[str(shard_path)] = stamp(shard_path)
        source_hashes[str(shard_path)] = file_hash(shard_path)
        with np.load(shard_path, allow_pickle=False) as shard:
            arrays = {field: shard[field] for field in ['record_index', 'key_id', 'n_atoms', 'formula', 'z', 'pos', *[config[0] for config in SCALARS.values()]]}
            require(len(arrays['record_index']) == shard_info['count'], f'Shard count mismatch {shard_path}')
            for row_offset, index_value in enumerate(arrays['record_index']):
                record_index = int(index_value)
                require(record_index not in cache_seen, f'Duplicate NPZ record {record_index}')
                cache_seen.add(record_index)
                if record_index not in records:
                    extra_cache.append(record_index)
                    continue
                record = records[record_index]
                atom_count = record['n_atoms']
                require(str(arrays['key_id'][row_offset]) == record['key_id'], f'NPZ key mismatch {record_index}')
                require(int(arrays['n_atoms'][row_offset]) == atom_count, f'NPZ atom count mismatch {record_index}')
                require(str(arrays['formula'][row_offset]) == record['formula'], f'NPZ formula mismatch {record_index}')
                require(0 < atom_count <= arrays['z'].shape[1], f'Invalid active atom count {record_index}')
                numbers = arrays['z'][row_offset, :atom_count]
                positions = arrays['pos'][row_offset, :atom_count]
                require(bool(np.all((numbers > 0) & (numbers <= 118)) and np.isfinite(positions).all()), f'Invalid NPZ geometry {record_index}')
                for field, (cache_field, _, _, _) in SCALARS.items():
                    require(float(arrays[cache_field][row_offset]) == record['values'][field], f'NPZ scalar mismatch {record_index} {field}')
                    cache_scalar_counts[field] += 1
                record['cache_geometry_sha256_float32'] = geometry_hash(numbers, positions)
                record['npz_path'] = str(shard_path)
                record['row_in_shard'] = row_offset
    require(set(records).issubset(cache_seen), 'Missing NPZ records')
    print(json_line({'stage': 'npz_checked', 'records': len(records), 'shards': len(manifest['shards'])}), end='', flush=True)
    pending_structures.mkdir()
    for prefix in sorted({key_id[:2] for key_id in by_key}):
        (pending_structures / prefix).mkdir()
    properties_seen = set()
    structures_seen = set()
    raw_scalar_counts = Counter()
    method_counts = Counter()
    status_counts = Counter()
    vibration_counts = Counter()
    raw_max_coordinate_rounding = 0.0
    written_count = 0
    pending_writes = deque()
    with ARCHIVE.open('rb') as raw_handle, ThreadPoolExecutor(max_workers=8) as writer:
        hashing_reader = HashingReader(raw_handle)
        with tarfile.open(fileobj=hashing_reader, mode='r|', bufsize=1024 * 1024) as archive:
            for member in archive:
                if not member.isfile():
                    continue
                parts = member.name.split('/')
                if len(parts) != 5 or parts[:2] != ['parsed_exact_v1', 'records']:
                    continue
                key_id = parts[3]
                if key_id not in by_key or parts[4] not in ('properties.json', 'structure.extxyz'):
                    continue
                require(parts[2] == key_id[:2], f'Unexpected member prefix {member.name}')
                record = by_key[key_id]
                record_index = record['record_index']
                payload = archive.extractfile(member).read()
                if parts[4] == 'properties.json':
                    require(key_id not in properties_seen, f'Duplicate raw properties {key_id}')
                    properties_seen.add(key_id)
                    properties = json.loads(payload)
                    require(properties['key_id'] == key_id, f'Raw properties key mismatch {key_id}')
                    require(hashlib.sha256(properties['hf_key'].encode()).hexdigest() == key_id, f'Raw key hash mismatch {key_id}')
                    require(properties['structure']['n_atoms'] == record['n_atoms'], f'Raw properties atom count mismatch {key_id}')
                    require(properties['structure']['unit'] == 'Angstrom', f'Unexpected coordinate unit {key_id}')
                    for field, (_, section, raw_field, precision) in SCALARS.items():
                        value = properties.get(section, {}).get(raw_field)
                        require(value is not None and math.isfinite(value), f'Missing or nonfinite raw scalar {key_id} {field}')
                        require(float(precision(value)) == record['values'][field], f'Raw scalar mismatch after cache precision {key_id} {field}')
                        raw_scalar_counts[field] += 1
                    source = properties['source']
                    configuration = {
                        'functional': source.get('functional'),
                        'basis_set': source.get('basis_set'),
                        'calculation_type': source.get('calculation_type'),
                        'scf_method': properties['scf'].get('method'),
                    }
                    method_counts[json.dumps(configuration, sort_keys=True)] += 1
                    status = {
                        'parser_status': properties.get('parser_status'),
                        'normal_termination': properties.get('normal_termination'),
                        'structure_source': properties['structure'].get('source'),
                    }
                    status_counts[json.dumps(status, sort_keys=True)] += 1
                    record['calculation'] = configuration
                    record['source_status'] = status
                    record['log_hash'] = source.get('log_hash')
                    frequencies = properties.get('vibrations', {}).get('frequencies_cm-1')
                    if frequencies and all(value is not None and math.isfinite(value) for value in frequencies):
                        minimum_frequency = min(frequencies)
                        record['minimum_frequency_cm-1'] = minimum_frequency
                        vibration_counts['finite_nonempty_frequencies'] += 1
                        vibration_counts['any_negative_frequency'] += minimum_frequency < 0
                    else:
                        record['minimum_frequency_cm-1'] = None
                        vibration_counts['missing_empty_or_nonfinite_frequencies'] += 1
                    continue
                require(key_id not in structures_seen, f'Duplicate raw structure {key_id}')
                structures_seen.add(key_id)
                lines, numbers, positions = parse_xyz(payload)
                header = dict(token.split('=', 1) for token in shlex.split(lines[1]) if '=' in token)
                require(header.get('key_id') == key_id, f'Raw structure header key mismatch {key_id}')
                require(hashlib.sha256(header.get('hf_key', '').encode()).hexdigest() == key_id, f'Raw structure header hash mismatch {key_id}')
                require(len(numbers) == record['n_atoms'], f'Raw structure atom count mismatch {key_id}')
                require(geometry_hash(numbers, positions) == record['cache_geometry_sha256_float32'], f'Raw structure does not reproduce NPZ coordinates {key_id}')
                formula_parts = re.findall(r'([A-Z][a-z]?)(\d*)', record['formula'])
                require(''.join(symbol + count for symbol, count in formula_parts) == record['formula'], f'Unsupported formula {key_id}')
                formula_counts = Counter()
                for symbol, count in formula_parts:
                    formula_counts[PERIODIC_TABLE.GetAtomicNumber(symbol)] += int(count or '1')
                require(formula_counts == Counter(numbers.tolist()), f'Raw structure composition mismatch {key_id}')
                raw_max_coordinate_rounding = max(raw_max_coordinate_rounding, float(np.max(np.abs(positions - positions.astype(np.float32).astype(np.float64)))))
                xyz_payload = (str(len(numbers)) + '\n\n' + '\n'.join(line.strip() for line in lines[2:len(numbers) + 2]) + '\n').encode('utf-8')
                relative_path = Path('structures') / key_id[:2] / (key_id + '.xyz')
                record['input_xyz_relative_path'] = str(relative_path)
                record['input_xyz_path'] = str(OUTPUT / relative_path)
                record['source_tar_member'] = member.name
                record['source_extxyz_sha256'] = hashlib.sha256(payload).hexdigest()
                record['structure_log_hash'] = header.get('log_hash')
                future = writer.submit(write_and_check, pending_structures / key_id[:2] / (key_id + '.xyz'), xyz_payload, numbers, positions)
                pending_writes.append((record, future))
                if len(pending_writes) >= 512:
                    completed_record, completed_future = pending_writes.popleft()
                    completed_record['input_xyz_sha256'] = completed_future.result()
                    written_count += 1
                    if written_count % 20000 == 0:
                        print(json_line({'stage': 'xyz_export', 'written_and_read_back': written_count, 'elapsed_seconds': round(time.monotonic() - started, 1)}), end='', flush=True)
        while hashing_reader.read(1024 * 1024):
            pass
        source_hashes[str(ARCHIVE)] = hashing_reader.digest.hexdigest()
        while pending_writes:
            completed_record, completed_future = pending_writes.popleft()
            completed_record['input_xyz_sha256'] = completed_future.result()
            written_count += 1
    require(properties_seen == by_key.keys(), 'Raw properties coverage incomplete')
    require(structures_seen == by_key.keys(), 'Raw structure coverage incomplete')
    require(written_count == len(records), 'XYZ output coverage incomplete')
    for record in records.values():
        require(record['log_hash'] and record['log_hash'] == record['structure_log_hash'], f'Properties and structure log binding mismatch {record["record_index"]}')
    for path_string, initial_stamp in snapshots.items():
        require(stamp(Path(path_string)) == initial_stamp, f'Source changed during export {path_string}')
    with pending_index.open('x') as handle:
        for record_index in sorted(records):
            record = dict(records[record_index])
            record['coordinate_unit'] = 'angstrom'
            record['geometry_source'] = 'raw_extxyz_without_coordinate_rounding'
            record['checks'] = {
                'raw_geometry_reproduces_npz_float32': True,
                'raw_scalars_reproduce_metadata_at_cache_precision': True,
                'xyz_readback_preserves_atom_order_and_coordinates': True,
            }
            handle.write(json_line(record))
    report = {
        'status': 'complete',
        'authority_records': len(records),
        'xyz_files': written_count,
        'split_counts': dict(Counter(splits.values())),
        'unique_stored_nonisomeric_smiles': len(representation_splits),
        'stored_nonisomeric_smiles_cross_split_overlap': 0,
        'metadata_records_excluded_by_authority': sorted(extra_metadata),
        'npz_records_excluded_by_authority': sorted(extra_cache),
        'metadata_old_split_disagreements': old_split_disagreements,
        'finite_metadata_values': dict(scalar_counts),
        'valid_binary_annotation_values': dict(flag_counts),
        'npz_metadata_scalar_matches': dict(cache_scalar_counts),
        'raw_metadata_scalar_matches_at_cache_precision': dict(raw_scalar_counts),
        'max_gap_identity_residual_eV': max_gap_residual,
        'max_polarizability_conversion_residual_A3': max_polarizability_residual,
        'raw_to_npz_max_coordinate_rounding_angstrom': raw_max_coordinate_rounding,
        'xyz_vs_raw_coordinate_error_angstrom': 0.0,
        'calculation_configurations': [dict(json.loads(configuration), count=count) for configuration, count in sorted(method_counts.items())],
        'source_status_counts': [dict(json.loads(status), count=count) for status, count in sorted(status_counts.items())],
        'vibration_diagnostics': dict(vibration_counts),
        'notes': [
            'XYZ files have blank comment lines and retain raw coordinate text and atom order.',
            'Completeness and source consistency are not independent DFT recalculations.',
            'No global 3D bond or stereochemistry validation is claimed.',
            'Normal termination alone does not establish a local minimum.',
            'Spectra are not exported or newly validated by this script.',
            'No train.jsonl, val.jsonl, preview.jsonl or query/response corpus has been generated.',
        ],
        'source_sha256': source_hashes,
        'source_stamps': snapshots,
        'structure_index_sha256': file_hash(pending_index),
        'export_script_sha256': file_hash(Path(__file__)),
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    pending_structures.rename(final_structures)
    pending_index.rename(final_index)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key not in ('source_sha256', 'source_stamps')}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
