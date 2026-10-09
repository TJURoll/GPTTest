import argparse
import csv
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np
from rdkit import Chem, rdBase
from rdkit.Chem import rdDetermineBonds, rdMolDescriptors
from rdkit.Chem.MolStandardize import rdMolStandardize


ROOT = Path('/mnt/e/Datasets/fg26')
OUTPUT = Path(__file__).resolve().parent
POLICY_DIRECTORY = Path('/home/lmy/SpectraAtom-LLM/scripts')
sys.path.insert(0, str(POLICY_DIRECTORY))
from build_fg_author_47_preview import apply_precedence, compile_smarts, raw_match_records, training_labels
from fg_author_47_policy import ACTIVE_FG26_LABELS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def untyped_graph(molecule):
    graph = nx.Graph()
    for atom in molecule.GetAtoms():
        graph.add_node(atom.GetIdx(), atomic_number=atom.GetAtomicNum())
    for bond in molecule.GetBonds():
        graph.add_edge(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())
    return graph


def find_mapping(reference, observed):
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        untyped_graph(reference),
        untyped_graph(observed),
        node_match=nx.algorithms.isomorphism.categorical_node_match('atomic_number', None),
    )
    return next(matcher.isomorphisms_iter(), None)


def canonical_without_stereo(molecule):
    molecule = Chem.RemoveHs(Chem.Mol(molecule))
    Chem.RemoveStereochemistry(molecule)
    return Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=False)


def resolved_labels(molecule, compiled):
    raw = raw_match_records(molecule, compiled)
    labels, kept, suppressions, _ = apply_precedence(raw)
    return training_labels(labels), raw, kept, suppressions


def check_representation_equivalence(reference_smiles, bond_perception):
    if any(check['exact_graph_matches_smiles_ignoring_stereo'] for check in bond_perception.values()):
        return {'matched': True, 'method': 'exact_nonisomeric_graph'}
    observed_smiles = bond_perception['charged_fragments'].get('canonical_smiles_nonisomeric')
    if observed_smiles is None:
        return {'matched': False, 'method': 'unresolved_bond_order_perception'}
    reference = Chem.MolFromSmiles(reference_smiles)
    observed = Chem.MolFromSmiles(observed_smiles)
    normalized_reference = canonical_without_stereo(rdMolStandardize.Normalize(reference))
    normalized_observed = canonical_without_stereo(rdMolStandardize.Normalize(observed))
    if normalized_reference == normalized_observed:
        return {
            'matched': True,
            'method': 'rdkit_normalize_functional_group_representation',
            'reference_before': reference_smiles,
            'observed_before': observed_smiles,
            'common_normalized_smiles': normalized_reference,
        }
    forms_checked = 0
    with rdBase.BlockLogs():
        supplier = Chem.ResonanceMolSupplier(reference, flags=Chem.ResonanceFlags.ALLOW_CHARGE_SEPARATION, maxStructs=256)
        for resonance in supplier:
            forms_checked += 1
            try:
                Chem.SanitizeMol(resonance)
            except Exception:
                continue
            if canonical_without_stereo(resonance) == observed_smiles:
                return {
                    'matched': True,
                    'method': 'rdkit_resonance_form_after_aromatic_sanitization',
                    'reference_before': reference_smiles,
                    'observed_before': observed_smiles,
                    'resonance_forms_checked': forms_checked,
                }
    return {
        'matched': False,
        'method': 'unresolved_bond_order_perception',
        'reference_before': reference_smiles,
        'observed_before': observed_smiles,
        'resonance_forms_checked': forms_checked,
        'note': 'Connectivity matches. This is not evidence of an incorrect FG label or structure pair; no record is discarded.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=OUTPUT / 'fg_sample_check_20260913.json')
    arguments = parser.parse_args()
    seed = 20260913
    generator = random.Random(seed)
    authority_path = ROOT / '04_training_data/repository_data/phase15_aux/canonical_selfies_by_record_index_v17_nonisomeric.jsonl'
    split_path = ROOT / '04_training_data/repository_data/split_maps/phase2_v26_record_split_map.jsonl'
    metadata_path = ROOT / '01_source_data/metadata/molecule_tables/fg26_molecule_metadata_v2_corrected_units.csv'
    index_path = OUTPUT / 'structure_index.jsonl'
    report_path = arguments.output
    require(not report_path.exists(), 'Refusing to overwrite a sample report')
    sources = [authority_path, split_path, metadata_path, index_path, POLICY_DIRECTORY / 'fg_author_47_policy.py', POLICY_DIRECTORY / 'build_fg_author_47_preview.py']
    initial_hashes = {str(path): sha256_file(path) for path in sources}
    with authority_path.open() as handle:
        authority = {json.loads(line)['record_index'] for line in handle}
    splits = {}
    with split_path.open() as handle:
        for line in handle:
            row = json.loads(line)
            splits[row['record_index']] = row['split']
    with metadata_path.open(newline='') as handle:
        metadata = {int(row['record_index']): row for row in csv.DictReader(handle) if int(row['record_index']) in authority}
    require(set(metadata) == authority == set(splits), 'Authority join failed')
    selections = []
    selected_ids = set()
    for split in ['train', 'val']:
        candidates = sorted(record_index for record_index in metadata if splits[record_index] == split)
        for record_index in generator.sample(candidates, 5):
            selections.append({'record_index': record_index, 'selection': 'random_' + split, 'pool_size': len(candidates)})
            selected_ids.add(record_index)
    target_groups = [
        ('sulfide_and_thiol', lambda row: row['fg_sulfide'] == row['fg_thiol'] == '1'),
        ('urea', lambda row: row['fg_urea'] == '1'),
        ('carbamate', lambda row: row['fg_carbamate'] == '1'),
        ('amide_and_amine', lambda row: row['fg_amide'] == row['fg_amine'] == '1'),
        ('nitro', lambda row: row['fg_nitro'] == '1'),
        ('azide', lambda row: row['fg_azide'] == '1'),
        ('thioester', lambda row: row['fg_thioester'] == '1'),
        ('allene', lambda row: row['fg_allene'] == '1'),
        ('aromatic_outside_old_pattern', lambda row: row['aromatic'] == '1' and row['aromatic_phase2_label'] == '0'),
        ('no_active_fg26', lambda row: not any(row['fg_' + label] == '1' for label in ACTIVE_FG26_LABELS)),
    ]
    for name, predicate in target_groups:
        candidates = sorted(record_index for record_index, row in metadata.items() if predicate(row) and record_index not in selected_ids)
        record_index = generator.choice(candidates)
        selections.append({'record_index': record_index, 'selection': name, 'pool_size_after_prior_selections': len(candidates)})
        selected_ids.add(record_index)
    structures = {}
    with index_path.open() as handle:
        for line in handle:
            row = json.loads(line)
            if row['record_index'] in selected_ids:
                structures[row['record_index']] = row
    require(set(structures) == selected_ids and len(selected_ids) == 20, 'Sample join failed')
    compiled = compile_smarts()
    results = []
    for selection in selections:
        record_index = selection['record_index']
        row = metadata[record_index]
        structure = structures[record_index]
        molecule = Chem.MolFromSmiles(row['canonical_smiles'])
        require(molecule is not None, f'Cannot parse source SMILES {record_index}')
        reference = Chem.AddHs(molecule)
        expected_labels = [label for label in ACTIVE_FG26_LABELS if row['fg_' + label] == '1']
        computed_labels, raw, kept, suppressions = resolved_labels(molecule, compiled)
        xyz_path = Path(structure['input_xyz_path'])
        payload = xyz_path.read_bytes()
        xyz = Chem.MolFromXYZBlock(payload.decode())
        require(xyz is not None, f'Cannot parse XYZ {record_index}')
        positions = np.asarray(xyz.GetConformer().GetPositions())
        numbers = np.array([atom.GetAtomicNum() for atom in xyz.GetAtoms()])
        offset = structure['row_in_shard']
        with np.load(structure['npz_path'], allow_pickle=False) as shard:
            atom_count = int(shard['n_atoms'][offset])
            cache_matches = bool(
                int(shard['record_index'][offset]) == record_index
                and str(shard['key_id'][offset]) == row['key_id'] == structure['key_id']
                and np.array_equal(numbers, shard['z'][offset, :atom_count])
                and np.array_equal(positions.astype(np.float32), shard['pos'][offset, :atom_count])
            )
        result = {
            **selection,
            'split': splits[record_index],
            'smiles': row['canonical_smiles'],
            'key_id': row['key_id'],
            'formula': row['formula'],
            'n_atoms': xyz.GetNumAtoms(),
            'input_xyz_path': str(xyz_path),
            'input_xyz_sha256': hashlib.sha256(payload).hexdigest(),
            'metadata_fg_labels': expected_labels,
            'recomputed_fg_labels': computed_labels,
            'raw_matched_labels': sorted({match['label'] for match in raw}),
            'suppression_evidence': suppressions,
            'metadata_aromatic': bool(int(row['aromatic'])),
            'recomputed_aromatic': any(atom.GetIsAromatic() for atom in molecule.GetAtoms()),
            'fg_labels_match_existing_policy': computed_labels == expected_labels,
            'formula_matches_smiles': rdMolDescriptors.CalcMolFormula(molecule) == row['formula'],
            'atom_counts_and_elements_match': reference.GetNumAtoms() == xyz.GetNumAtoms() and Counter(atom.GetAtomicNum() for atom in reference.GetAtoms()) == Counter(numbers.tolist()),
            'xyz_hash_matches_export_index': hashlib.sha256(payload).hexdigest() == structure['input_xyz_sha256'],
            'xyz_matches_npz': cache_matches,
        }
        connectivities = {}
        chosen_mapping = None
        for name, use_vdw in [('connect_the_dots', False), ('covalent_radii_factor_1_3', True)]:
            perceived = Chem.Mol(xyz)
            try:
                rdDetermineBonds.DetermineConnectivity(perceived, useVdw=use_vdw, covFactor=1.3)
                mapping = find_mapping(reference, perceived)
                connectivities[name] = {
                    'connectivity_isomorphic': mapping is not None,
                    'reference_bonds_including_h': reference.GetNumBonds(),
                    'perceived_bonds_including_h': perceived.GetNumBonds(),
                    'reference_to_xyz_atom_mapping_zero_based': mapping,
                }
                if chosen_mapping is None and mapping is not None:
                    chosen_mapping = mapping
            except Exception as error:
                connectivities[name] = {'connectivity_isomorphic': False, 'error': type(error).__name__ + ': ' + str(error)}
        result['independent_xyz_connectivity'] = connectivities
        bond_perception = {}
        reference_canonical = canonical_without_stereo(molecule)
        for name, allow_charged in [('charged_fragments', True), ('radical_fragments', False)]:
            perceived = Chem.Mol(xyz)
            try:
                with rdBase.BlockLogs():
                    rdDetermineBonds.DetermineBonds(
                        perceived,
                        charge=Chem.GetFormalCharge(molecule),
                        allowChargedFragments=allow_charged,
                        embedChiral=False,
                        useVdw=False,
                        maxIterations=10000,
                    )
                    Chem.SanitizeMol(perceived)
                canonical = canonical_without_stereo(perceived)
                inferred_labels, _, _, _ = resolved_labels(Chem.RemoveHs(perceived), compiled)
                bond_perception[name] = {
                    'canonical_smiles_nonisomeric': canonical,
                    'exact_graph_matches_smiles_ignoring_stereo': canonical == reference_canonical,
                    'fg_labels_from_independently_perceived_xyz': inferred_labels,
                    'fg_labels_match_metadata': inferred_labels == expected_labels,
                    'aromatic_matches_metadata': any(atom.GetIsAromatic() for atom in perceived.GetAtoms()) == result['metadata_aromatic'],
                }
            except Exception as error:
                bond_perception[name] = {'exact_graph_matches_smiles_ignoring_stereo': False, 'error': type(error).__name__ + ': ' + str(error)}
        result['reference_canonical_smiles_nonisomeric'] = reference_canonical
        result['independent_xyz_bond_order_perception'] = bond_perception
        result['bond_representation_followup'] = check_representation_equivalence(reference_canonical, bond_perception)
        result['fg_atom_evidence'] = []
        if chosen_mapping is not None:
            for match in kept:
                if match['label'] not in ACTIVE_FG26_LABELS:
                    continue
                atom_ids = set(match['atoms'])
                distances = []
                for bond in molecule.GetBonds():
                    begin = bond.GetBeginAtomIdx()
                    end = bond.GetEndAtomIdx()
                    if begin in atom_ids and end in atom_ids:
                        xyz_begin = chosen_mapping[begin]
                        xyz_end = chosen_mapping[end]
                        distances.append({
                            'xyz_atoms_one_based': [xyz_begin + 1, xyz_end + 1],
                            'elements': [molecule.GetAtomWithIdx(begin).GetSymbol(), molecule.GetAtomWithIdx(end).GetSymbol()],
                            'bond_type_from_source_smiles': str(bond.GetBondType()),
                            'observed_distance_angstrom': float(np.linalg.norm(positions[xyz_begin] - positions[xyz_end])),
                        })
                centers = []
                for atom_index in match['center_atoms']:
                    xyz_index = chosen_mapping[atom_index]
                    neighbors = []
                    for neighbor in reference.GetAtomWithIdx(atom_index).GetNeighbors():
                        neighbor_xyz = chosen_mapping[neighbor.GetIdx()]
                        neighbors.append({'xyz_atom_one_based': neighbor_xyz + 1, 'element': neighbor.GetSymbol(), 'distance_angstrom': float(np.linalg.norm(positions[xyz_index] - positions[neighbor_xyz]))})
                    centers.append({'xyz_atom_one_based': xyz_index + 1, 'element': reference.GetAtomWithIdx(atom_index).GetSymbol(), 'neighbors': neighbors})
                result['fg_atom_evidence'].append({'label': match['label'], 'xyz_atoms_one_based': [chosen_mapping[atom_index] + 1 for atom_index in match['atoms']], 'matched_bond_distances': distances, 'centers': centers})
        results.append(result)
        print(json.dumps({
            'record_index': record_index,
            'selection': selection['selection'],
            'labels': expected_labels,
            'fg_policy_match': result['fg_labels_match_existing_policy'],
            'connectivity': {name: check['connectivity_isomorphic'] for name, check in connectivities.items()},
            'bond_order_graph_match': {name: check['exact_graph_matches_smiles_ignoring_stereo'] for name, check in bond_perception.items()},
        }), flush=True)
    require(all(sha256_file(path) == initial_hashes[str(path)] for path in sources), 'An input changed during the audit')
    summary = {
        'records': len(results),
        'split_counts': dict(Counter(result['split'] for result in results)),
        'fg_labels_match_existing_policy': sum(result['fg_labels_match_existing_policy'] for result in results),
        'aromatic_matches_existing_corrected_flag': sum(result['metadata_aromatic'] == result['recomputed_aromatic'] for result in results),
        'xyz_identity_composition_and_cache_checks_pass': sum(all(result[field] for field in ['formula_matches_smiles', 'atom_counts_and_elements_match', 'xyz_hash_matches_export_index', 'xyz_matches_npz']) for result in results),
        'connectivity_isomorphic_both_methods': sum(all(check['connectivity_isomorphic'] for check in result['independent_xyz_connectivity'].values()) for result in results),
        'connectivity_isomorphic_at_least_one_method': sum(any(check['connectivity_isomorphic'] for check in result['independent_xyz_connectivity'].values()) for result in results),
        'exact_bond_order_graph_recovered_at_least_one_method': sum(any(check['exact_graph_matches_smiles_ignoring_stereo'] for check in result['independent_xyz_bond_order_perception'].values()) for result in results),
        'bond_graph_matches_including_representation_equivalence': sum(result['bond_representation_followup']['matched'] for result in results),
        'bond_representation_followup_counts': dict(Counter(result['bond_representation_followup']['method'] for result in results)),
        'unresolved_bond_order_record_indices': [result['record_index'] for result in results if not result['bond_representation_followup']['matched']],
        'observed_fg_labels': sorted({label for result in results for label in result['metadata_fg_labels']}),
    }
    report = {
        'status': 'sample_audit_completed_not_full_library_certification',
        'seed': seed,
        'rdkit_version': rdBase.rdkitVersion,
        'selection_method': 'Five random train and five random val records, then ten predefined targeted strata with no duplicate records.',
        'summary': summary,
        'source_sha256': initial_hashes,
        'script_sha256': sha256_file(Path(__file__)),
        'scope_notes': [
            'Original SMARTS, precedence policy, labels, split and structures remain unchanged.',
            'XYZ connectivity is compared using element-labelled graph isomorphism, not assumed atom order.',
            'Bond-order perception is an independent heuristic; failure is not proof that the source structure or label is wrong.',
            'RDKit Normalize and bounded resonance enumeration are used only for structure comparison, never to change the original FG policy or labels.',
            'Stereochemistry, thermodynamic stability, DFT accuracy and alternate functional-group definitions are not assessed.',
            'Distances are recorded as observations, not used as new functional-group definitions or fitted pass thresholds.',
            'The sample is partly targeted and does not estimate whole-library error rates.',
        ],
        'samples': results,
    }
    with report_path.open('x') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({'report_path': str(report_path), 'summary': summary}, indent=2), flush=True)


if __name__ == '__main__':
    main()
