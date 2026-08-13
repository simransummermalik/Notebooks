# Every finding from my Pathview Plus checks

This is my complete list from the test run. I kept this page because the shorter
report only talks about the biggest patterns, while this table shows every finding
and the exact test that reproduced it.

I split the list into two groups. P1 contains the things I think should be checked
first because they affect a main workflow or an advertised feature. P2/P3 contains
smaller issues, input checks, and edge cases. A feature gap is listed separately
from a reproduced bug because it can mean that a feature was started but is not
connected yet.

## Totals

- Different reproduced findings: **79**
- Different feature gaps: **7**

## P1 — findings I would look at first

| ID | Type | What I reproduced | Exact test(s) |
|---|---|---|---|
| PV-BUG-004 | reproduced finding | cached files cannot bypass live species lookup | `tests.test_public_core::test_fully_cached_human_pathway_does_not_require_network` |
| PV-BUG-006 | reproduced finding | map_null=False does not remove unmapped rows when a data table exists | `tests.test_public_core::test_map_null_false_removes_unmapped_pathway_nodes` |
| PV-BUG-008 | reproduced finding | core returns dict while documented highlighting requires PathwayResult | `tests.test_public_core::test_core_result_supports_documented_highlighting_interface` |
| PV-BUG-009 | reproduced finding | mapped node table drops the exploded kegg_names identifier | `tests.test_mapping_and_colors::test_mapped_node_table_retains_kegg_names`<br>`tests.test_public_core::test_core_gene_table_contains_highlighting_identifier_column` |
| PV-BUG-012 | reproduced finding | group aggregation UDF receives scalar elements under current Polars | `tests.test_mapping_and_colors::test_all_advertised_aggregations_work[max_abs]`<br>`tests.test_mapping_and_colors::test_all_advertised_aggregations_work[random]` |
| PV-BUG-023 | reproduced finding | parser locates a namespaced map but searches its glyphs/arcs without namespace | `tests.test_parsers::test_standard_namespaced_sbgn_is_parsed` |
| PV-BUG-029 | reproduced finding | compound y coordinates are flipped while gene y coordinates are effectively not | `tests.test_rendering::test_gene_and_compound_use_same_coordinate_system` |
| PV-BUG-030 | reproduced finding | compound KGML width is treated as radius instead of diameter | `tests.test_rendering::test_compound_width_is_the_full_display_diameter` |
| PV-BUG-034 | reproduced finding | bbox_inches='tight' crops/rescales native output instead of preserving KEGG pixels | `tests.test_rendering::test_native_output_preserves_background_dimensions` |
| PV-BUG-038 | reproduced finding | graph/PDF renderer uses only the first experiment color | `tests.test_rendering::test_graph_renderer_preserves_two_state_node_colors` |
| PV-BUG-039 | reproduced finding | highlights flip y but native gene painting does not, so borders miss noncentral nodes | `tests.test_highlighting_and_splines::test_highlight_border_uses_same_coordinates_as_native_gene_node` |
| PV-BUG-045 | reproduced finding | duplicated phantom/repeated Catmull-Rom points cause zero denominators and NaNs | `tests.test_highlighting_and_splines::test_catmull_rom_documented_inputs_are_finite[points0]`<br>`tests.test_highlighting_and_splines::test_catmull_rom_documented_inputs_are_finite[points1]`<br>`tests.test_highlighting_and_splines::test_catmull_rom_documented_inputs_are_finite[points2]` |
| PV-BUG-052 | reproduced finding | CLI unconditionally calls gene_data.cast even for compound-only input | `tests.test_cli_and_integrations::test_cli_compound_only_workflow` |
| PV-BUG-058 | reproduced finding | MyGene batch endpoint is /v3/query, not coded /v3/querymany | `tests.test_cli_and_integrations::test_mygene_uses_documented_batch_query_endpoint` |
| PV-BUG-065 | reproduced finding | SBGN downloaders accept HTTP 200 HTML pages as successful pathway files | `tests.test_cli_and_integrations::test_sbgn_downloaders_reject_html[download_reactome-R-HSA-109582]`<br>`tests.test_cli_and_integrations::test_sbgn_downloaders_reject_html[download_metacyc-PWY-7210]` |
| PV-BUG-074 | reproduced finding | Reactome SBGN file exporter route is coded as /exporter/sbgn/{id}.sbgn instead of /exporter/event/{id}.sbgn | `tests.test_cli_and_integrations::test_reactome_downloader_uses_file_exporter_route` |
| PV-BUG-075 | reproduced finding | _add_symbol_labels joins a SYMBOL column but never replaces the rendered label | `tests.test_public_core::test_map_symbol_updates_the_label_used_by_renderers` |
| PV-FEATURE-003 | feature gap | main SVG renderer receives no relation data and emits no pathway edges | `tests.test_rendering::test_main_svg_renderer_includes_pathway_edges` |
| PV-FEATURE-004 | feature gap | graph renderer builds nodes only; KGML relations are not passed into it | `tests.test_rendering::test_graph_renderer_contains_relations` |
| PV-FEATURE-007 | feature gap | non-KEGG database detection/download/parsing is not wired through pathview() | `tests.test_cli_and_integrations::test_core_routes_reactome_ids_to_reactome_pipeline` |

## P2/P3 — smaller issues and edge cases

| ID | Type | What I reproduced | Exact test(s) |
|---|---|---|---|
| PV-BUG-001 | reproduced finding | setup.py/distribution is 2.0.2 but pathview.__version__ is 2.0.0 | `tests.test_public_core::test_distribution_and_runtime_versions_match` |
| PV-BUG-002 | reproduced finding | --no-kegg-native with output_format='png' silently writes graph PDF | `tests.test_public_core::test_non_native_png_request_produces_png` |
| PV-BUG-003 | reproduced finding | Python API does not validate output_format; unknown values become PDF | `tests.test_public_core::test_python_api_rejects_unknown_output_format[jpg]`<br>`tests.test_public_core::test_python_api_rejects_unknown_output_format[PNG]`<br>`tests.test_public_core::test_python_api_rejects_unknown_output_format[]`<br>`tests.test_public_core::test_python_api_rejects_unknown_output_format[banana]` |
| PV-BUG-005 | reproduced finding | a partial color config replaces defaults instead of merging per molecule type | `tests.test_public_core::test_partial_color_dictionary_keeps_unspecified_defaults` |
| PV-BUG-007 | reproduced finding | min_nnodes counts pathway layout nodes, not nodes matched by input data | `tests.test_public_core::test_min_nnodes_is_based_on_input_matches` |
| PV-BUG-010 | reproduced finding | pathway prefixes that conflict with species are concatenated, not rejected | `tests.test_public_core::test_conflicting_pathway_prefix_is_rejected` |
| PV-BUG-011 | reproduced finding | empty KGML produces a schema-less frame and core crashes before graceful skip | `tests.test_public_core::test_empty_cached_pathway_is_skipped_cleanly` |
| PV-BUG-013 | reproduced finding | mol_sum casts data IDs to strings but not mapping IDs | `tests.test_mapping_and_colors::test_mol_sum_normalizes_both_id_column_types` |
| PV-BUG-014 | reproduced finding | null mapping targets are aggregated into a null output ID | `tests.test_mapping_and_colors::test_null_mapping_targets_are_removed` |
| PV-BUG-015 | reproduced finding | duplicated mapping pairs duplicate the input value before aggregation | `tests.test_mapping_and_colors::test_duplicate_mapping_pairs_do_not_double_count` |
| PV-BUG-016 | reproduced finding | entrez_gnodes is unused and species prefixes are always stripped | `tests.test_mapping_and_colors::test_kegg_gene_ids_can_be_mapped_without_stripping_prefix` |
| PV-BUG-017 | reproduced finding | negative experiment count is silently accepted | `tests.test_mapping_and_colors::test_simulation_rejects_negative_experiment_count` |
| PV-BUG-018 | reproduced finding | decimal strings are parsed as hexadecimal numbers | `tests.test_mapping_and_colors::test_decimal_string_values_mean_the_same_as_decimal_numbers` |
| PV-BUG-019 | reproduced finding | namespace-qualified KGML child tags are not dispatched | `tests.test_parsers::test_namespace_qualified_kgml_is_parsed` |
| PV-BUG-020 | reproduced finding | duplicate KGML entry IDs silently overwrite earlier entries | `tests.test_parsers::test_duplicate_kgml_entry_ids_are_rejected` |
| PV-BUG-021 | reproduced finding | line graphics coords are ignored and replaced with zero/default geometry | `tests.test_parsers::test_kgml_line_graphics_coordinates_are_preserved` |
| PV-BUG-022 | reproduced finding | node_info(empty pathway) has no stable columns/schema | `tests.test_parsers::test_empty_kgml_node_table_has_standard_schema` |
| PV-BUG-024 | reproduced finding | SBGN namespace is hard-coded to 0.2 and does not accept other valid versions | `tests.test_parsers::test_sbgn_namespace_version_is_discovered_from_document` |
| PV-BUG-025 | reproduced finding | nested state-variable glyph is also promoted to a top-level biological node | `tests.test_parsers::test_state_variable_is_metadata_not_a_top_level_node` |
| PV-BUG-026 | reproduced finding | standard <clone/> element is not detected; code checks an attribute instead | `tests.test_parsers::test_standard_sbgn_clone_marker_is_detected` |
| PV-BUG-027 | reproduced finding | Bezier control <point> children inside SBGN <next> are discarded | `tests.test_parsers::test_sbgn_arc_control_points_are_preserved` |
| PV-BUG-028 | reproduced finding | empty SBGN conversion returns a schema-less DataFrame | `tests.test_parsers::test_empty_sbgn_dataframe_has_unified_schema` |
| PV-BUG-031 | reproduced finding | compound height is ignored and all compounds are forced to width-based circles | `tests.test_rendering::test_compound_renderer_respects_elliptical_height` |
| PV-BUG-032 | reproduced finding | documented/default named highlight colors are parsed as six-digit hex | `tests.test_highlighting_and_splines::test_default_named_node_highlight_color_works`<br>`tests.test_rendering::test_native_color_converter_accepts_named_matplotlib_colors` |
| PV-BUG-033 | reproduced finding | three-digit CSS hex colors are not accepted | `tests.test_rendering::test_native_color_converter_accepts_short_hex` |
| PV-BUG-035 | reproduced finding | SVG document title is not XML-escaped | `tests.test_rendering::test_svg_pathway_title_with_special_characters_is_valid` |
| PV-BUG-036 | reproduced finding | SVG clip IDs interpolate unescaped node identifiers | `tests.test_rendering::test_svg_ellipse_accepts_special_node_identifiers` |
| PV-BUG-037 | reproduced finding | empty SVG fill list renders text but no node shape | `tests.test_rendering::test_svg_node_with_no_fill_values_still_has_a_visible_shape` |
| PV-BUG-040 | reproduced finding | highlight opacity argument is ignored | `tests.test_highlighting_and_splines::test_border_opacity_blends_with_existing_pixels` |
| PV-BUG-041 | reproduced finding | change_labels records metadata but does not alter the saved image | `tests.test_highlighting_and_splines::test_change_labels_visibly_changes_rendered_result` |
| PV-BUG-042 | reproduced finding | edge highlighting builds positions from genes only | `tests.test_highlighting_and_splines::test_edge_highlighting_supports_compounds` |
| PV-BUG-043 | reproduced finding | requested one-pixel line is drawn two pixels thick | `tests.test_highlighting_and_splines::test_line_thickness_one_is_exactly_one_pixel` |
| PV-BUG-044 | reproduced finding | save() does not infer PDF from path and writes PNG bytes to a .pdf name | `tests.test_highlighting_and_splines::test_save_infers_format_from_file_extension` |
| PV-BUG-046 | reproduced finding | obstacles=None forces every routing mode to a straight two-point line | `tests.test_highlighting_and_splines::test_curved_routing_works_without_obstacle_list` |
| PV-BUG-047 | reproduced finding | obstacles argument is not consulted by routing implementation | `tests.test_highlighting_and_splines::test_edge_route_avoids_supplied_obstacle` |
| PV-BUG-048 | reproduced finding | orthogonal routing delegates to broken Catmull-Rom implementation | `tests.test_highlighting_and_splines::test_orthogonal_route_is_finite` |
| PV-BUG-049 | reproduced finding | unknown routing mode silently falls back to straight | `tests.test_highlighting_and_splines::test_unknown_routing_mode_is_rejected` |
| PV-BUG-050 | reproduced finding | smooth_path_svg tension parameter is unused | `tests.test_highlighting_and_splines::test_smooth_svg_tension_changes_curve` |
| PV-BUG-051 | reproduced finding | nonfinite curve values are serialized directly into SVG | `tests.test_highlighting_and_splines::test_nonfinite_curve_is_rejected_before_svg_serialization` |
| PV-BUG-053 | reproduced finding | CLI reports pathway row count as 'nodes mapped', including null rows | `tests.test_cli_and_integrations::test_cli_reports_non_null_mapped_count` |
| PV-BUG-054 | reproduced finding | upstream feature script fails when run directly because of relative imports | `tests.test_cli_and_integrations::test_upstream_feature_script_runs_as_documented` |
| PV-BUG-055 | reproduced finding | promised common-name lookup requires exact equality with full KEGG description | `tests.test_cli_and_integrations::test_species_resolution_accepts_common_name` |
| PV-BUG-056 | reproduced finding | invalid KEGG file types fail with internal KeyError instead of validation error | `tests.test_cli_and_integrations::test_kegg_download_rejects_invalid_file_type` |
| PV-BUG-057 | reproduced finding | KEGG downloader trusts any HTTP 200 body without format/content validation | `tests.test_cli_and_integrations::test_kegg_download_rejects_html_error_page_with_status_200[xml]`<br>`tests.test_cli_and_integrations::test_kegg_download_rejects_html_error_page_with_status_200[png]` |
| PV-BUG-059 | reproduced finding | nested MyGene fields are stringified as Python dicts instead of extracting IDs | `tests.test_cli_and_integrations::test_mygene_nested_uniprot_result_extracts_accession` |
| PV-BUG-060 | reproduced finding | core forwards KEGG code 'hsa' where MyGene documents common names/taxonomy IDs | `tests.test_cli_and_integrations::test_symbol_mapping_translates_kegg_species_to_mygene_species` |
| PV-BUG-061 | reproduced finding | KEGG chemical conversion uses alias 'cpd' where API specifies 'compound' | `tests.test_cli_and_integrations::test_compound_mapping_uses_documented_kegg_database_name` |
| PV-BUG-062 | reproduced finding | already-prefixed compound IDs receive a duplicate source prefix | `tests.test_cli_and_integrations::test_compound_mapping_normalizes_prefixed_input` |
| PV-BUG-063 | reproduced finding | SMP prefix detection accepts malformed arbitrary IDs | `tests.test_cli_and_integrations::test_database_detection_validates_smpdb_identifier` |
| PV-BUG-064 | reproduced finding | database detection is unexpectedly case-sensitive | `tests.test_cli_and_integrations::test_database_detection_is_case_insensitive` |
| PV-BUG-066 | reproduced finding | list_reactome_pathways hardcodes Homo sapiens in URL | `tests.test_cli_and_integrations::test_reactome_listing_uses_requested_species` |
| PV-BUG-067 | reproduced finding | SVG output unnecessarily requires/downloads a KEGG PNG when kegg_native=True | `tests.test_public_core::test_svg_core_needs_only_cached_xml` |
| PV-BUG-068 | reproduced finding | KGML shape='circle' is sent to SVG but only shape='ellipse' renders an ellipse | `tests.test_rendering::test_svg_renders_kgml_circle_as_circle` |
| PV-BUG-069 | reproduced finding | all-transparent SVG nodes are forcibly recolored gray | `tests.test_rendering::test_svg_preserves_transparent_unmapped_nodes` |
| PV-BUG-070 | reproduced finding | compound-only native color-key layout leaves a blank visible ticked subplot | `tests.test_rendering::test_compound_only_color_key_has_no_blank_subplot` |
| PV-BUG-071 | reproduced finding | graph color key always uses gene limits/colors, even for compound-only plots | `tests.test_rendering::test_compound_only_graph_uses_compound_color_scale` |
| PV-BUG-072 | reproduced finding | highlight drawing cannot assign RGB tuples into RGBA arrays | `tests.test_highlighting_and_splines::test_highlighting_supports_rgba_pathway_images` |
| PV-BUG-073 | reproduced finding | dynamic label-change metadata is lost when another layer is chained | `tests.test_highlighting_and_splines::test_label_changes_survive_later_highlight_layers` |
| PV-BUG-076 | reproduced finding | invalid node_sum ValueError is swallowed by node_map and core still returns output | `tests.test_public_core::test_invalid_node_sum_is_rejected_by_python_api` |
| PV-BUG-077 | reproduced finding | --simulate branch silently ignores a supplied --cpd-data file | `tests.test_cli_and_integrations::test_cli_simulation_can_be_combined_with_compound_data` |
| PV-BUG-078 | reproduced finding | MyGene returnall dictionary response is iterated as if it were a list of hits | `tests.test_cli_and_integrations::test_mygene_returnall_response_shape_is_supported` |
| PV-BUG-079 | reproduced finding | wordwrap width=0 with break_word=True makes no progress and loops forever | `tests.test_mapping_and_colors::test_hard_wordwrap_rejects_zero_width_instead_of_hanging` |
| PV-FEATURE-001 | feature gap | discrete is accepted by public APIs but ignored by node_color | `tests.test_mapping_and_colors::test_discrete_setting_changes_color_mapping_mode` |
| PV-FEATURE-002 | feature gap | SBGNGlyph exposes unit_of_information but parser never populates it | `tests.test_parsers::test_sbgn_unit_of_information_is_parsed` |
| PV-FEATURE-005 | feature gap | PANTHER downloader is an explicit unimplemented stub | `tests.test_cli_and_integrations::test_panther_downloader_returns_path` |
| PV-FEATURE-006 | feature gap | SMPDB downloader is an explicit unimplemented stub | `tests.test_cli_and_integrations::test_smpdb_downloader_returns_path` |

## Files I used for this list

If someone wants to check a row or use the results in another program:

- `BUGS.json` has the same list in a machine-readable format.
- `results/audit-results.csv` has every test case, including the ones that passed.
- `results/junit.xml` can be used by continuous-integration tools.
- `results/pytest-output.txt` has the full warnings and traceback summaries.
