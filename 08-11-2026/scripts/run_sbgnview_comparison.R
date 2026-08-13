#!/usr/bin/env Rscript

# Controlled R SBGNview baseline for the August 11 Pathview Plus v3 test.
#
# This script is offline and reproducible: it uses only frozen SBGN files from
# the checked-out Python source plus the mapping table bundled with the official
# Bioconductor package. All evidence is written below results/sbgnview.

args_all <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args_all, value = TRUE)
if (length(script_arg) != 1L) stop("Run this file with Rscript")

script_file <- normalizePath(sub("^--file=", "", script_arg[[1]]), mustWork = TRUE)
day_root <- normalizePath(file.path(dirname(script_file), ".."), mustWork = TRUE)
workspace_root <- normalizePath(file.path(day_root, ".."), mustWork = TRUE)
r_library <- normalizePath(
  file.path(workspace_root, "pygage-pathview-validation", ".r-library"),
  mustWork = TRUE
)
.libPaths(unique(c(r_library, .libPaths())))

required_packages <- c("SBGNview", "SBGNview.data", "xml2", "jsonlite", "rsvg")
missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]
if (length(missing_packages) > 0L) {
  stop("Missing installed R package(s): ", paste(missing_packages, collapse = ", "))
}

suppressPackageStartupMessages(library(SBGNview))

result_root <- file.path(day_root, "results", "sbgnview")
dir.create(result_root, recursive = TRUE, showWarnings = FALSE)

fixture_root <- file.path(day_root, "sources", "pathview-plus", "tests", "fixtures")
fixtures <- c(
  bare = file.path(fixture_root, "P00001.new.layout.sbgn"),
  namespaced = file.path(fixture_root, "P00001.namespaced.sbgn"),
  ports = file.path(fixture_root, "ports_pd.sbgn")
)
shared_input <- file.path(day_root, "data", "P00001-shared-control-treatment.csv")
required_files <- c(fixtures, shared_input)
if (!all(file.exists(required_files))) {
  stop("Missing frozen input(s): ", paste(required_files[!file.exists(required_files)], collapse = ", "))
}

data("sbgn.xmls", package = "SBGNview.data", envir = .GlobalEnv)
data("pathwayCommons_SYMBOL", package = "SBGNview.data", envir = .GlobalEnv)
data("pathways.info", package = "SBGNview", envir = .GlobalEnv)

relative_to_workspace <- function(path) {
  absolute <- normalizePath(path, mustWork = FALSE)
  prefix <- paste0(normalizePath(workspace_root, mustWork = TRUE), .Platform$file.sep)
  sub(paste0("^", prefix), "", absolute)
}

sha256_file <- function(path) {
  answer <- system2(
    "/usr/bin/shasum",
    c("-a", "256", shQuote(normalizePath(path, mustWork = TRUE))),
    stdout = TRUE,
    stderr = TRUE
  )
  if (!identical(attr(answer, "status"), NULL) || length(answer) < 1L) {
    stop("Could not calculate SHA-256 for ", path)
  }
  strsplit(answer[[1]], "[[:space:]]+")[[1]][[1]]
}

scalar_slot <- function(object, name, default = "") {
  if (!name %in% slotNames(object)) return(default)
  value <- slot(object, name)
  if (length(value) == 0L) default else paste(as.character(value), collapse = "|")
}

xml_summary <- function(path) {
  document <- xml2::read_xml(path)
  namespace <- xml2::xml_ns(document)
  namespace_value <- if (length(namespace) == 0L) {
    "none"
  } else {
    values <- unname(as.character(namespace))
    values <- values[nzchar(values)]
    if (length(values) == 0L) "none" else values[[1]]
  }
  list(
    xml_namespace = namespace_value,
    xml_glyph_elements = length(xml2::xml_find_all(document, "//*[local-name()='glyph']")),
    xml_arc_elements = length(xml2::xml_find_all(document, "//*[local-name()='arc']"))
  )
}

build_sbgn <- function(path, output_prefix, output_formats = "svg", ...) {
  SBGNview(
    input.sbgn = basename(path),
    sbgn.dir = dirname(path),
    output.file = output_prefix,
    output.formats = output_formats,
    show.pathway.name = FALSE,
    ...
  )
}

glyph_signature <- function(object) {
  glyphs <- object$data[[1]]$glyphs.list
  rows <- lapply(glyphs, function(glyph) {
    data.frame(
      id = scalar_slot(glyph, "id"),
      glyph_class = scalar_slot(glyph, "glyph.class"),
      label = scalar_slot(glyph, "label"),
      x = scalar_slot(glyph, "x"),
      y = scalar_slot(glyph, "y"),
      w = scalar_slot(glyph, "w"),
      h = scalar_slot(glyph, "h"),
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}

arc_signature <- function(object) {
  arcs <- object$data[[1]]$arcs.list
  rows <- lapply(arcs, function(arc) {
    data.frame(
      id = scalar_slot(arc, "id"),
      arc_class = scalar_slot(arc, "arc.class"),
      source = scalar_slot(arc, "source"),
      target = scalar_slot(arc, "target"),
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}

inspect_object <- function(scenario, path, object) {
  parsed <- object$data[[1]]
  glyphs <- parsed$glyphs.list
  classes <- vapply(glyphs, scalar_slot, character(1), name = "glyph.class")
  xml <- xml_summary(path)
  data.frame(
    scenario = scenario,
    input_file = relative_to_workspace(path),
    input_sha256 = sha256_file(path),
    xml_namespace = xml$xml_namespace,
    xml_glyph_elements = xml$xml_glyph_elements,
    xml_arc_elements = xml$xml_arc_elements,
    r_glyph_objects = length(glyphs),
    r_render_arc_segments = length(parsed$arcs.list),
    compartments = sum(classes == "compartment"),
    macromolecules = sum(classes == "macromolecule"),
    simple_chemicals = sum(classes == "simple chemical"),
    processes = sum(classes == "process"),
    complexes = sum(classes == "complex"),
    unspecified_entities = sum(classes == "unspecified entity"),
    ports_as_objects = sum(vapply(glyphs, function(glyph) methods::is(glyph, "port"), logical(1))),
    state_variables_as_objects = sum(classes == "state variable"),
    clone_markers = sum(vapply(glyphs, function(glyph) {
      "clone" %in% slotNames(glyph) && length(slot(glyph, "clone")) > 0L
    }, logical(1))),
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
}

output_evidence <- function(path, scenario) {
  info <- file.info(path)
  if (is.na(info$size) || info$size <= 0L) stop("Expected non-empty output: ", path)
  data.frame(
    implementation = "R SBGNview",
    scenario = scenario,
    format = toupper(sub("^\\.", "", tools::file_ext(path))),
    output_file = relative_to_workspace(path),
    bytes = unname(info$size),
    sha256 = sha256_file(path),
    stringsAsFactors = FALSE
  )
}

print_and_record <- function(object, scenario) {
  print(object)
  prefixes <- vapply(object$data, function(item) {
    item$render.sbgn.parameters.list$output.file
  }, character(1))
  formats <- unique(c("svg", object$output.formats))
  paths <- unlist(lapply(prefixes, function(prefix) paste0(prefix, ".", formats)))
  do.call(rbind, lapply(paths, output_evidence, scenario = scenario))
}

cat("Building the two namespace controls...\n")
bare_object <- build_sbgn(
  fixtures[["bare"]],
  file.path(result_root, "r-namespace-bare")
)
namespaced_object <- build_sbgn(
  fixtures[["namespaced"]],
  file.path(result_root, "r-namespace-namespaced")
)

stopifnot(length(bare_object$data[[1]]$glyphs.list) == 78L)
stopifnot(length(bare_object$data[[1]]$arcs.list) == 83L)
stopifnot(identical(glyph_signature(bare_object), glyph_signature(namespaced_object)))
stopifnot(identical(arc_signature(bare_object), arc_signature(namespaced_object)))

cat("Building the small ports/state/clone control...\n")
ports_object <- build_sbgn(
  fixtures[["ports"]],
  file.path(result_root, "r-structural")
)
ports_metrics <- inspect_object(
  "ports, state, and clone fixture",
  fixtures[["ports"]],
  ports_object
)
stopifnot(ports_metrics$xml_glyph_elements == 6L)
stopifnot(ports_metrics$xml_arc_elements == 3L)
stopifnot(ports_metrics$r_glyph_objects == 8L)
stopifnot(ports_metrics$r_render_arc_segments == 4L)
stopifnot(ports_metrics$ports_as_objects == 2L)
stopifnot(ports_metrics$state_variables_as_objects == 1L)
stopifnot(ports_metrics$clone_markers == 1L)

shared <- read.csv(shared_input, check.names = FALSE, stringsAsFactors = FALSE)
expected_shared <- data.frame(
  symbol = c("COMT", "DDC", "TH", "DBH", "PNMT", "SLC18A2", "SLC6A3"),
  Control = c(-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5),
  Treatment = c(1.5, 1.0, 0.5, 0.0, -0.5, -1.0, -1.5),
  check.names = FALSE,
  stringsAsFactors = FALSE
)
stopifnot(identical(shared, expected_shared))
gene_data <- as.matrix(shared[, c("Control", "Treatment")])
rownames(gene_data) <- shared$symbol

human_symbol_map <- pathwayCommons_SYMBOL[
  pathwayCommons_SYMBOL$species == "Homo sapiens",
  c("SYMBOL", "pathwayCommons")
]

cat("Building the shared seven-gene, two-condition result...\n")
mapped_object <- build_sbgn(
  fixtures[["bare"]],
  file.path(result_root, "r-two-state"),
  output_formats = c("svg", "png"),
  gene.data = gene_data,
  gene.id.type = "SYMBOL",
  sbgn.gene.id.type = "pathwayCommons",
  id.mapping.gene = human_symbol_map
)

mapped_glyphs <- mapped_object$data[[1]]$glyphs.list
glyph_classes <- vapply(mapped_glyphs, scalar_slot, character(1), name = "glyph.class")
is_mapped <- vapply(mapped_glyphs, function(glyph) {
  user_data <- slot(glyph, "user.data")
  is.numeric(user_data) && length(user_data) > 0L && any(!is.na(user_data))
}, logical(1))
mapped_indexes <- which(is_mapped)
stopifnot(length(mapped_indexes) == 12L)
stopifnot(sum(glyph_classes == "macromolecule") == 19L)
stopifnot(all(glyph_classes[mapped_indexes] == "macromolecule"))

mapped_rows <- lapply(mapped_indexes, function(index) {
  glyph <- mapped_glyphs[[index]]
  glyph_id <- scalar_slot(glyph, "id")
  base_glyph_id <- sub("_Complex_.*$", "", glyph_id)
  user_data <- as.numeric(slot(glyph, "user.data"))
  source_symbols <- unique(human_symbol_map$SYMBOL[
    human_symbol_map$pathwayCommons %in% c(glyph_id, base_glyph_id) &
      human_symbol_map$SYMBOL %in% shared$symbol
  ])
  data.frame(
    entry_id = glyph_id,
    glyph_label = scalar_slot(glyph, "label"),
    glyph_class = scalar_slot(glyph, "glyph.class"),
    input_symbols = paste(source_symbols, collapse = ";"),
    Control = user_data[[1]],
    Treatment = user_data[[2]],
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
})
mapped_table <- do.call(rbind, mapped_rows)
used_symbols <- sort(unique(unlist(strsplit(mapped_table$input_symbols, ";", fixed = TRUE))))
used_symbols <- used_symbols[nzchar(used_symbols)]
stopifnot(setequal(used_symbols, shared$symbol))
stopifnot(all(vapply(mapped_glyphs[mapped_indexes], function(glyph) {
  identical(names(slot(glyph, "user.data")), c("Control", "Treatment"))
}, logical(1))))

write.table(
  mapped_table,
  file.path(result_root, "r-mapped-nodes.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

structural_rows <- lapply(ports_object$data[[1]]$glyphs.list, function(glyph) {
  data.frame(
    object_class = class(glyph)[[1]],
    entry_id = scalar_slot(glyph, "id"),
    glyph_label = scalar_slot(glyph, "label"),
    glyph_class = scalar_slot(glyph, "glyph.class"),
    clone_children = if ("clone" %in% slotNames(glyph)) length(slot(glyph, "clone")) else 0L,
    stringsAsFactors = FALSE
  )
})
write.table(
  do.call(rbind, structural_rows),
  file.path(result_root, "r-structural-objects.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

metric_rows <- rbind(
  inspect_object("P00001 bare XML", fixtures[["bare"]], bare_object),
  inspect_object("P00001 default namespace", fixtures[["namespaced"]], namespaced_object),
  ports_metrics
)
write.table(
  metric_rows,
  file.path(result_root, "r-metrics.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

output_rows <- rbind(
  print_and_record(bare_object, "bare namespace control"),
  print_and_record(namespaced_object, "default namespace control"),
  print_and_record(ports_object, "ports/state/clone fixture"),
  print_and_record(mapped_object, "shared two-state mapping")
)
write.table(
  output_rows,
  file.path(result_root, "output-manifest-r.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

official_fixture <- system.file(
  "extdata", "P00001.new.layout.sbgn", package = "SBGNview", mustWork = TRUE
)
official_fixture_sha256 <- sha256_file(official_fixture)
frozen_fixture_sha256 <- sha256_file(fixtures[["bare"]])
stopifnot(official_fixture_sha256 == frozen_fixture_sha256)

package_versions <- data.frame(
  component = c(
    "R", "Bioconductor", "SBGNview", "SBGNview.data", "rsvg", "xml2", "igraph"
  ),
  version = c(
    paste(R.version$major, R.version$minor, sep = "."),
    if (requireNamespace("BiocManager", quietly = TRUE)) {
      as.character(BiocManager::version())
    } else {
      NA_character_
    },
    as.character(packageVersion("SBGNview")),
    as.character(packageVersion("SBGNview.data")),
    as.character(packageVersion("rsvg")),
    as.character(packageVersion("xml2")),
    if (requireNamespace("igraph", quietly = TRUE)) {
      as.character(packageVersion("igraph"))
    } else {
      NA_character_
    }
  ),
  stringsAsFactors = FALSE
)
write.table(
  package_versions,
  file.path(result_root, "r-package-versions.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

librsvg_version <- tryCatch(
  system2("rsvg-convert", "--version", stdout = TRUE, stderr = TRUE)[[1]],
  error = function(error) NA_character_
)

comparison <- list(
  title = "Official R SBGNview frozen comparison evidence",
  generated_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
  offline = TRUE,
  environment = list(
    r = R.version.string,
    bioconductor = package_versions$version[package_versions$component == "Bioconductor"],
    SBGNview = as.character(packageVersion("SBGNview")),
    SBGNview_data = as.character(packageVersion("SBGNview.data")),
    rsvg = as.character(packageVersion("rsvg")),
    system_librsvg = librsvg_version,
    library = r_library
  ),
  official_bundled_data = list(
    pathways_info_rows = nrow(pathways.info),
    pathwayCommons_SYMBOL_rows = nrow(pathwayCommons_SYMBOL),
    human_pathwayCommons_SYMBOL_rows = nrow(human_symbol_map),
    official_P00001_fixture = official_fixture,
    official_P00001_sha256 = official_fixture_sha256,
    frozen_P00001_sha256 = frozen_fixture_sha256,
    frozen_fixture_is_byte_identical = TRUE
  ),
  shared_input = list(
    file = relative_to_workspace(shared_input),
    sha256 = sha256_file(shared_input),
    ids = shared$symbol,
    conditions = c("Control", "Treatment")
  ),
  namespace_parity = list(
    passed = TRUE,
    r_glyph_objects_each = 78L,
    r_render_arc_segments_each = 83L,
    identical_glyph_signatures = TRUE,
    identical_arc_signatures = TRUE
  ),
  mapping = list(
    mapped_macromolecule_glyphs = length(mapped_indexes),
    eligible_macromolecule_glyphs = sum(glyph_classes == "macromolecule"),
    input_ids_used = length(used_symbols),
    input_ids_total = nrow(shared),
    used_symbols = used_symbols,
    value_columns = c("Control", "Treatment"),
    every_mapped_glyph_kept_both_named_values = TRUE,
    mapped_rows = mapped_table
  ),
  structural_fixture = list(
    xml_glyph_elements = ports_metrics$xml_glyph_elements,
    xml_logical_arcs = ports_metrics$xml_arc_elements,
    r_glyph_like_objects = ports_metrics$r_glyph_objects,
    r_render_arc_segments = ports_metrics$r_render_arc_segments,
    port_objects = ports_metrics$ports_as_objects,
    state_variable_objects = ports_metrics$state_variables_as_objects,
    clone_markers = ports_metrics$clone_markers
  ),
  outputs = output_rows,
  assertions = list(
    P00001_bare_and_namespaced_identical = TRUE,
    P00001_matches_official_bundled_fixture_byte_for_byte = TRUE,
    ports_state_and_clone_preserved = TRUE,
    shared_mapping_12_of_19_macromolecule_glyphs = TRUE,
    shared_mapping_7_of_7_input_ids = TRUE,
    two_condition_values_preserved = TRUE,
    all_outputs_nonempty = TRUE
  )
)
jsonlite::write_json(
  comparison,
  file.path(result_root, "r-comparison.json"),
  pretty = TRUE,
  auto_unbox = TRUE,
  na = "null",
  dataframe = "rows"
)

cat("PASS: official R SBGNview comparison\n")
cat("  namespace parity: 78 glyph objects, 83 arc objects\n")
cat("  shared mapping: 12/19 macromolecule glyphs; 7/7 input IDs used\n")
cat("  ports fixture: 6 XML glyphs -> 8 render objects; 3 arcs -> 4 segments\n")
for (path in output_rows$output_file) cat("  wrote ", path, "\n", sep = "")
