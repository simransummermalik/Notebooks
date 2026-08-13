#!/usr/bin/env Rscript

# Controlled R pathview baseline for the August 11 Pathview Plus v3 comparison.
#
# This script runs offline. It copies the frozen hsa04110 files from
# the already-installed R pathview package and the frozen hsa00020 KGML fixture
# from the checked-out Pathview Plus v3 source. It never downloads from KEGG and
# never writes into either source package.

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

required_packages <- c("pathview", "png", "jsonlite")
missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]
if (length(missing_packages) > 0L) {
  stop("Missing installed R package(s): ", paste(missing_packages, collapse = ", "))
}

suppressPackageStartupMessages(library(pathview))

out <- file.path(day_root, "results", "r-pathview")
cache <- file.path(out, "cache")
dir.create(out, recursive = TRUE, showWarnings = FALSE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)

old_dir <- setwd(out)
on.exit(setwd(old_dir), add = TRUE)

relative_to_day <- function(path) {
  absolute <- normalizePath(path, mustWork = FALSE)
  prefix <- paste0(normalizePath(day_root, mustWork = TRUE), .Platform$file.sep)
  sub(paste0("^", prefix), "08-11-2026/", absolute)
}

file_evidence <- function(path) {
  info <- file.info(path)
  if (is.na(info$size)) return(list(path = relative_to_day(path), exists = FALSE))
  list(
    path = relative_to_day(path),
    exists = TRUE,
    bytes = unname(info$size),
    md5 = unname(tools::md5sum(path)[[1]])
  )
}

png_evidence <- function(path) {
  evidence <- file_evidence(path)
  if (!isTRUE(evidence$exists)) return(evidence)
  image <- png::readPNG(path)
  evidence$width_px <- dim(image)[[2]]
  evidence$height_px <- dim(image)[[1]]
  evidence$channels <- dim(image)[[3]]
  evidence
}

safe_command <- function(command, args) {
  output <- tryCatch(
    system2(command, args, stdout = TRUE, stderr = FALSE),
    error = function(error) character()
  )
  if (length(output) == 0L) NA_character_ else trimws(output[[1]])
}

v3_source <- file.path(day_root, "sources", "pathview-plus")
v3_pyproject <- file.path(v3_source, "pyproject.toml")
v3_version_line <- grep(
  "^version[[:space:]]*=",
  readLines(v3_pyproject, warn = FALSE),
  value = TRUE
)
v3_version <- sub('^version[[:space:]]*=[[:space:]]*"([^"]+)".*$', "\\1", v3_version_line[[1]])
v3_commit <- safe_command("git", c("-C", v3_source, "rev-parse", "HEAD"))

report <- list(
  title = "R pathview controlled comparison for Pathview Plus v3",
  run_date = format(Sys.Date(), "%Y-%m-%d"),
  generated_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
  offline = TRUE,
  environment = list(
    r_version = R.version.string,
    platform = R.version$platform,
    pathview_version = as.character(utils::packageVersion("pathview")),
    pathview_library = normalizePath(find.package("pathview"), mustWork = TRUE),
    r_library_reused_read_only = r_library,
    bioconductor_version = if (requireNamespace("BiocManager", quietly = TRUE)) {
      as.character(BiocManager::version())
    } else {
      NA_character_
    },
    rgraphviz_version = if (requireNamespace("Rgraphviz", quietly = TRUE)) {
      as.character(utils::packageVersion("Rgraphviz"))
    } else {
      NA_character_
    },
    pathview_plus_version_compared = v3_version,
    pathview_plus_commit_compared = v3_commit
  ),
  fixture_policy = paste(
    "No network calls. hsa04110 comes from R pathview extdata;",
    "hsa00020 KGML comes from the pinned Pathview Plus v3 test fixture."
  ),
  checks = list()
)

record_check <- function(name, status, seconds = 0, details = NULL, error = NULL) {
  if (!status %in% c("pass", "fail", "skipped")) stop("Invalid check status: ", status)
  item <- list(
    id = sprintf("R%02d", length(report$checks) + 1L),
    name = name,
    status = status,
    seconds = round(seconds, 4)
  )
  if (!is.null(details)) item$details <- details
  if (!is.null(error)) item$error <- error
  report$checks[[length(report$checks) + 1L]] <<- item
  suffix <- if (is.null(error)) "" else paste0(": ", error)
  cat(toupper(status), " ", item$id, " ", name, suffix, "\n", sep = "")
  invisible(item)
}

run_check <- function(name, expression) {
  start <- proc.time()[["elapsed"]]
  item <- tryCatch(
    {
      warning_messages <- character()
      details <- withCallingHandlers(
        force(expression),
        warning = function(warning) {
          warning_messages <<- c(warning_messages, conditionMessage(warning))
          invokeRestart("muffleWarning")
        }
      )
      if (length(warning_messages) > 0L) {
        warning_table <- sort(table(warning_messages), decreasing = TRUE)
        details$warnings <- lapply(names(warning_table), function(message) {
          list(message = message, count = unname(warning_table[[message]]))
        })
        details$warning_count <- length(warning_messages)
      }
      record_check(name, "pass", proc.time()[["elapsed"]] - start, details = details)
    },
    error = function(error) {
      record_check(
        name,
        "fail",
        proc.time()[["elapsed"]] - start,
        error = paste(class(error)[[1]], conditionMessage(error), sep = ": ")
      )
    }
  )
  invisible(item)
}

run_skip <- function(name, reason) {
  record_check(name, "skipped", details = list(reason = reason))
}

assert_true <- function(condition, message) {
  if (!isTRUE(condition)) stop(message, call. = FALSE)
}

copy_fixture <- function(source, destination) {
  assert_true(file.exists(source), paste("Fixture does not exist:", source))
  copied <- file.copy(source, destination, overwrite = TRUE, copy.mode = FALSE)
  assert_true(copied && file.exists(destination), paste("Could not copy fixture:", source))
  destination
}

palette <- list(
  limit = list(gene = 2, cpd = 2),
  bins = list(gene = 11, cpd = 11),
  both.dirs = list(gene = TRUE, cpd = TRUE),
  low = list(gene = "#00FF00", cpd = "#0000FF"),
  mid = list(gene = "#BEBEBE", cpd = "#BEBEBE"),
  high = list(gene = "#FF0000", cpd = "#FFFF00")
)

base_arguments <- function(pathway_id = "04110", native = TRUE) {
  list(
    pathway.id = pathway_id,
    species = "hsa",
    gene.idtype = "entrez",
    cpd.idtype = "kegg",
    kegg.dir = cache,
    kegg.native = native,
    map.symbol = FALSE,
    map.cpdname = FALSE,
    same.layer = TRUE,
    plot.col.key = FALSE,
    new.signature = FALSE,
    limit = palette$limit,
    bins = palette$bins,
    both.dirs = palette$both.dirs,
    low = palette$low,
    mid = palette$mid,
    high = palette$high
  )
}

row_for_id <- function(plot_data, identifier) {
  mapped <- as.character(plot_data$all.mapped)
  which(!is.na(mapped) & vapply(strsplit(mapped, "[[:space:]]*,[[:space:]]*"), function(ids) {
    identifier %in% ids
  }, logical(1)))
}

crop_node <- function(image, x, y, width, height, padding = 0) {
  rows <- max(1L, floor(y - height / 2 - padding)):min(dim(image)[[1]], ceiling(y + height / 2 + padding))
  cols <- max(1L, floor(x - width / 2 - padding)):min(dim(image)[[2]], ceiling(x + width / 2 + padding))
  image[rows, cols, , drop = FALSE]
}

hex_rgb <- function(hex) {
  grDevices::col2rgb(hex)[, 1] / 255
}

color_mask <- function(image, hex, tolerance = 45 / 255) {
  target <- hex_rgb(hex)
  channels <- image[, , seq_len(min(3L, dim(image)[[3]])), drop = FALSE]
  abs(channels[, , 1] - target[[1]]) <= tolerance &
    abs(channels[, , 2] - target[[2]]) <= tolerance &
    abs(channels[, , 3] - target[[3]]) <= tolerance
}

count_color <- function(image, hex, tolerance = 45 / 255) {
  sum(color_mask(image, hex, tolerance))
}

split_image_columns <- function(image, pieces) {
  width <- dim(image)[[2]]
  lapply(seq_len(pieces), function(index) {
    start <- floor((index - 1L) * width / pieces) + 1L
    end <- floor(index * width / pieces)
    image[, start:end, , drop = FALSE]
  })
}

write_crop <- function(image, path) {
  png::writePNG(image, target = path)
  png_evidence(path)
}

official_xml_source <- system.file("extdata", "hsa04110.xml", package = "pathview")
official_png_source <- system.file("extdata", "hsa04110.png", package = "pathview")
official_xml <- file.path(cache, "hsa04110.xml")
official_png <- file.path(cache, "hsa04110.png")
tca_xml_source <- file.path(v3_source, "tests", "fixtures", "hsa00020.xml")
tca_xml <- file.path(cache, "hsa00020.xml")
tca_png <- file.path(cache, "hsa00020.png")

run_check("environment and package versions", {
  assert_true(as.character(utils::packageVersion("pathview")) == "1.52.0", "Unexpected R pathview version")
  assert_true(v3_version == "3.1.0", "Unexpected Pathview Plus version")
  assert_true(nzchar(v3_commit) && nchar(v3_commit) == 40L, "Could not identify the v3 source commit")
  report$environment
})

run_check("frozen offline hsa04110 fixture", {
  copy_fixture(official_xml_source, official_xml)
  copy_fixture(official_png_source, official_png)
  original <- png_evidence(official_png)
  assert_true(original$width_px == 1039L && original$height_px == 801L, "Unexpected official fixture dimensions")
  list(
    source = "R pathview 1.52.0 installed extdata",
    xml = file_evidence(official_xml),
    png = original
  )
})

one_result <- NULL
one_output <- file.path(out, "hsa04110.r-one-state.png")
run_check("one-state native pathway", {
  gene_vector <- c("1029" = -2, "7157" = -1.6, "1956" = -1.2)
  arguments <- c(
    list(gene.data = gene_vector, out.suffix = "r-one-state", multi.state = TRUE),
    base_arguments("04110", TRUE)
  )
  one_result <<- do.call(pathview, arguments)
  assert_true(file.exists(one_output) && file.info(one_output)$size > 0, "One-state PNG was not written")
  rows <- row_for_id(one_result$plot.data.gene, "1029")
  assert_true(length(rows) > 0L, "Entrez 1029 did not map")
  assert_true(all(one_result$plot.data.gene[rows, "mol.data"] == -2, na.rm = TRUE), "Entrez 1029 value mismatch")
  csv <- file.path(out, "hsa04110.r-one-state.gene-nodes.csv")
  utils::write.csv(one_result$plot.data.gene, csv, row.names = FALSE)
  list(
    input = list(`1029` = -2, `7157` = -1.6, `1956` = -1.2),
    mapped_gene_nodes = sum(!is.na(one_result$plot.data.gene$mol.data)),
    output = png_evidence(one_output),
    node_table = file_evidence(csv)
  )
})

two_result <- NULL
two_output <- file.path(out, "hsa04110.r-half-half.multi.png")
two_crop_file <- file.path(out, "hsa04110.r-half-half.CDKN2A-crop.png")
run_check("two-state half-and-half native pathway", {
  gene_matrix <- matrix(
    c(-2, 2, -1.6, 1.6, -1.2, 1.2),
    nrow = 3,
    byrow = TRUE,
    dimnames = list(c("1029", "7157", "1956"), c("Classical", "Basal"))
  )
  arguments <- c(
    list(gene.data = gene_matrix, out.suffix = "r-half-half", multi.state = TRUE),
    base_arguments("04110", TRUE)
  )
  two_result <<- do.call(pathview, arguments)
  assert_true(file.exists(two_output) && file.info(two_output)$size > 0, "Two-state PNG was not written")
  rows <- row_for_id(two_result$plot.data.gene, "1029")
  assert_true(length(rows) > 0L, "Entrez 1029 did not map")
  assert_true(all(two_result$plot.data.gene[rows, "Classical"] == -2, na.rm = TRUE), "Classical value mismatch")
  assert_true(all(two_result$plot.data.gene[rows, "Basal"] == 2, na.rm = TRUE), "Basal value mismatch")

  row <- two_result$plot.data.gene[rows[[1]], , drop = FALSE]
  image <- png::readPNG(two_output)
  crop <- crop_node(image, row$x, row$y, row$width, row$height)
  pieces <- split_image_columns(crop, 2L)
  counts <- list(
    left_green = count_color(pieces[[1]], "#00FF00"),
    left_red = count_color(pieces[[1]], "#FF0000"),
    right_green = count_color(pieces[[2]], "#00FF00"),
    right_red = count_color(pieces[[2]], "#FF0000")
  )
  assert_true(counts$left_green > counts$left_red && counts$left_green > 0L, "Left half is not the low/green state")
  assert_true(counts$right_red > counts$right_green && counts$right_red > 0L, "Right half is not the high/red state")
  crop_evidence <- write_crop(crop, two_crop_file)
  csv <- file.path(out, "hsa04110.r-half-half.gene-nodes.csv")
  utils::write.csv(two_result$plot.data.gene, csv, row.names = FALSE)
  list(
    input_state_order = c("Classical=-2 (left)", "Basal=+2 (right)"),
    cdkn2a_geometry = list(x = row$x, y = row$y, width = row$width, height = row$height),
    cdkn2a_color_counts = counts,
    output = png_evidence(two_output),
    crop = crop_evidence,
    node_table = file_evidence(csv)
  )
})

shared_result <- NULL
shared_output <- file.path(out, "hsa04110.r-shared-control-treatment.multi.png")
run_check("shared Control/Treatment dataset for the R-Python notebook", {
  shared_ids <- c("1017", "1019", "1021", "595", "7157")
  shared_matrix <- matrix(
    c(
      -1.5, 1.5,
      -0.7, 0.7,
       0.0, 0.0,
       0.8, -0.8,
       1.4, -1.4
    ),
    nrow = 5,
    byrow = TRUE,
    dimnames = list(shared_ids, c("Control", "Treatment"))
  )
  input_table <- data.frame(
    entrez_id = shared_ids,
    Control = shared_matrix[, "Control"],
    Treatment = shared_matrix[, "Treatment"],
    stringsAsFactors = FALSE,
    row.names = NULL
  )
  input_csv <- file.path(out, "shared-hsa04110-control-treatment-input.csv")
  utils::write.csv(input_table, input_csv, row.names = FALSE)

  arguments <- c(
    list(
      gene.data = shared_matrix,
      out.suffix = "r-shared-control-treatment",
      multi.state = TRUE
    ),
    base_arguments("04110", TRUE)
  )
  shared_result <<- do.call(pathview, arguments)
  assert_true(file.exists(shared_output) && file.info(shared_output)$size > 0, "Shared-dataset PNG was not written")

  mapped_rows_by_id <- lapply(shared_ids, function(identifier) {
    row_for_id(shared_result$plot.data.gene, identifier)
  })
  names(mapped_rows_by_id) <- shared_ids
  missing_ids <- names(mapped_rows_by_id)[lengths(mapped_rows_by_id) == 0L]
  assert_true(length(missing_ids) == 0L, paste("Shared Entrez IDs did not map:", paste(missing_ids, collapse = ", ")))
  selected_rows <- sort(unique(unlist(mapped_rows_by_id, use.names = FALSE)))
  selected_nodes <- shared_result$plot.data.gene[selected_rows, , drop = FALSE]
  assert_true(all(is.finite(selected_nodes$Control)), "A selected node lacks a Control value")
  assert_true(all(is.finite(selected_nodes$Treatment)), "A selected node lacks a Treatment value")

  node_csv <- file.path(out, "hsa04110.r-shared-control-treatment.gene-nodes.csv")
  selected_csv <- file.path(out, "hsa04110.r-shared-control-treatment.selected-nodes.csv")
  utils::write.csv(shared_result$plot.data.gene, node_csv, row.names = FALSE)
  utils::write.csv(selected_nodes, selected_csv, row.names = FALSE)
  list(
    input_values = split(input_table[, c("Control", "Treatment")], input_table$entrez_id),
    state_order = c("Control (left)", "Treatment (right)"),
    requested_entrez_ids = shared_ids,
    mapped_row_indices_by_id = mapped_rows_by_id,
    note = "If multiple input genes share one KEGG node, R pathview reports the node-level aggregate in the selected-node table.",
    selected_node_rows = nrow(selected_nodes),
    output = png_evidence(shared_output),
    input_csv = file_evidence(input_csv),
    all_node_table = file_evidence(node_csv),
    selected_node_table = file_evidence(selected_csv)
  )
})

three_result <- NULL
three_output <- file.path(out, "hsa04110.r-three-state.multi.png")
three_crop_file <- file.path(out, "hsa04110.r-three-state.CDKN2A-crop.png")
run_check("three-state native pathway", {
  gene_matrix <- matrix(
    c(-2, 0, 2, -1.6, 0, 1.6, -1.2, 0, 1.2),
    nrow = 3,
    byrow = TRUE,
    dimnames = list(c("1029", "7157", "1956"), c("Low", "Middle", "High"))
  )
  arguments <- c(
    list(gene.data = gene_matrix, out.suffix = "r-three-state", multi.state = TRUE),
    base_arguments("04110", TRUE)
  )
  three_result <<- do.call(pathview, arguments)
  assert_true(file.exists(three_output) && file.info(three_output)$size > 0, "Three-state PNG was not written")
  rows <- row_for_id(three_result$plot.data.gene, "1029")
  assert_true(length(rows) > 0L, "Entrez 1029 did not map")
  row <- three_result$plot.data.gene[rows[[1]], , drop = FALSE]
  assert_true(identical(as.numeric(row[, c("Low", "Middle", "High")]), c(-2, 0, 2)), "Three-state values or order changed")

  image <- png::readPNG(three_output)
  crop <- crop_node(image, row$x, row$y, row$width, row$height)
  pieces <- split_image_columns(crop, 3L)
  counts <- list(
    left = list(green = count_color(pieces[[1]], "#00FF00"), gray = count_color(pieces[[1]], "#BEBEBE"), red = count_color(pieces[[1]], "#FF0000")),
    middle = list(green = count_color(pieces[[2]], "#00FF00"), gray = count_color(pieces[[2]], "#BEBEBE"), red = count_color(pieces[[2]], "#FF0000")),
    right = list(green = count_color(pieces[[3]], "#00FF00"), gray = count_color(pieces[[3]], "#BEBEBE"), red = count_color(pieces[[3]], "#FF0000"))
  )
  assert_true(counts$left$green > max(counts$left$gray, counts$left$red), "First third is not low/green")
  assert_true(counts$middle$gray > max(counts$middle$green, counts$middle$red), "Middle third is not middle/gray")
  assert_true(counts$right$red > max(counts$right$green, counts$right$gray), "Last third is not high/red")
  crop_evidence <- write_crop(crop, three_crop_file)
  csv <- file.path(out, "hsa04110.r-three-state.gene-nodes.csv")
  utils::write.csv(three_result$plot.data.gene, csv, row.names = FALSE)
  list(
    input_state_order = c("Low=-2 (left)", "Middle=0 (middle)", "High=+2 (right)"),
    cdkn2a_geometry = list(x = row$x, y = row$y, width = row$width, height = row$height),
    cdkn2a_color_counts = counts,
    output = png_evidence(three_output),
    crop = crop_evidence,
    node_table = file_evidence(csv)
  )
})

run_check("native PNG dimensions and gene geometry", {
  outputs <- c(one_output, two_output, three_output)
  assert_true(all(file.exists(outputs)), "A required native PNG is missing")
  dimensions <- lapply(outputs, png_evidence)
  dimension_pairs <- vapply(dimensions, function(item) paste(item$width_px, item$height_px, sep = "x"), character(1))
  assert_true(all(dimension_pairs == "1039x801"), "A native result changed the frozen background dimensions")

  rows <- row_for_id(two_result$plot.data.gene, "1029")
  assert_true(length(rows) > 0L, "Entrez 1029 was unavailable for the geometry check")
  row <- two_result$plot.data.gene[rows[[1]], , drop = FALSE]
  expected <- c(x = 532, y = 124, width = 46, height = 17)
  observed <- c(x = row$x, y = row$y, width = row$width, height = row$height)
  assert_true(isTRUE(all.equal(unname(observed), unname(expected))), "R gene node geometry differs from the frozen KGML")
  list(
    expected_and_observed_gene_geometry = as.list(expected),
    source_dimensions = png_evidence(official_png),
    result_dimensions = dimensions
  )
})

graph_output <- file.path(out, "hsa04110.r-graph.multi.pdf")
if (!requireNamespace("Rgraphviz", quietly = TRUE)) {
  run_skip("two-state Graphviz pathway PDF", "Rgraphviz is not installed in the reused R library")
} else {
  run_check("two-state Graphviz pathway PDF", {
    gene_matrix <- matrix(
      c(-2, 2, -1.6, 1.6, -1.2, 1.2),
      nrow = 3,
      byrow = TRUE,
      dimnames = list(c("1029", "7157", "1956"), c("Classical", "Basal"))
    )
    arguments <- c(
      list(gene.data = gene_matrix, out.suffix = "r-graph", multi.state = TRUE),
      base_arguments("04110", FALSE)
    )
    graph_result <- do.call(pathview, arguments)
    assert_true(file.exists(graph_output) && file.info(graph_output)$size > 1000, "Graphviz PDF was not written or is empty")
    connection <- file(graph_output, "rb")
    on.exit(close(connection), add = TRUE)
    signature <- rawToChar(readBin(connection, "raw", n = 4L))
    assert_true(signature == "%PDF", "Graph result does not have a PDF signature")
    list(
      states = c("Classical", "Basal"),
      graph_gene_node_rows = nrow(graph_result$plot.data.gene),
      pdf_signature = signature,
      output = file_evidence(graph_output)
    )
  })
}

gene_cpd_result <- NULL
gene_cpd_output <- file.path(out, "hsa00020.r-gene-compound.multi.png")
gene_cpd_geometry <- NULL
run_check("gene and compound data on one native pathway", {
  copy_fixture(tca_xml_source, tca_xml)
  blank <- array(1, dim = c(800L, 1000L, 4L))
  png::writePNG(blank, target = tca_png)

  gene_matrix <- matrix(
    c(-2, 2, -1.6, 1.6, -1.2, 1.2),
    nrow = 3,
    byrow = TRUE,
    dimnames = list(c("1738", "1743", "1737"), c("Low", "High"))
  )
  cpd_matrix <- matrix(
    c(-2, 2, 2, -2),
    nrow = 2,
    byrow = TRUE,
    dimnames = list(c("C00022", "C00122"), c("Low", "High"))
  )
  arguments <- c(
    list(
      gene.data = gene_matrix,
      cpd.data = cpd_matrix,
      out.suffix = "r-gene-compound",
      multi.state = TRUE
    ),
    base_arguments("00020", TRUE)
  )
  gene_cpd_result <<- do.call(pathview, arguments)
  assert_true(file.exists(gene_cpd_output) && file.info(gene_cpd_output)$size > 0, "Gene/compound PNG was not written")

  gene_rows <- row_for_id(gene_cpd_result$plot.data.gene, "1738")
  compound_rows <- row_for_id(gene_cpd_result$plot.data.cpd, "C00022")
  assert_true(length(gene_rows) > 0L, "Entrez 1738 did not map")
  assert_true(length(compound_rows) > 0L, "KEGG compound C00022 did not map")
  assert_true(all(gene_cpd_result$plot.data.gene[gene_rows, "Low"] == -2, na.rm = TRUE), "Gene Low value mismatch")
  assert_true(all(gene_cpd_result$plot.data.cpd[compound_rows, "Low"] == -2, na.rm = TRUE), "Compound Low value mismatch")

  gene_csv <- file.path(out, "hsa00020.r-gene-compound.gene-nodes.csv")
  cpd_csv <- file.path(out, "hsa00020.r-gene-compound.compound-nodes.csv")
  utils::write.csv(gene_cpd_result$plot.data.gene, gene_csv, row.names = FALSE)
  utils::write.csv(gene_cpd_result$plot.data.cpd, cpd_csv, row.names = FALSE)
  list(
    controlled_background = list(description = "1000x800 blank white PNG made locally", evidence = png_evidence(tca_png)),
    gene_input = list(`1738` = c(Low = -2, High = 2), `1743` = c(Low = -1.6, High = 1.6), `1737` = c(Low = -1.2, High = 1.2)),
    compound_input = list(C00022 = c(Low = -2, High = 2), C00122 = c(Low = 2, High = -2)),
    mapped_gene_rows = sum(!is.na(gene_cpd_result$plot.data.gene$Low)),
    mapped_compound_rows = sum(!is.na(gene_cpd_result$plot.data.cpd$Low)),
    output = png_evidence(gene_cpd_output),
    gene_node_table = file_evidence(gene_csv),
    compound_node_table = file_evidence(cpd_csv)
  )
})

run_check("native compound center uses top-left image coordinates", {
  assert_true(!is.null(gene_cpd_result), "Gene/compound render did not complete")
  compound_rows <- row_for_id(gene_cpd_result$plot.data.cpd, "C00022")
  assert_true(length(compound_rows) > 0L, "C00022 was unavailable for geometry checks")
  row <- gene_cpd_result$plot.data.cpd[compound_rows[[1]], , drop = FALSE]
  image <- png::readPNG(gene_cpd_output)

  search_radius <- 20L
  row_indices <- max(1L, round(row$y) - search_radius):min(dim(image)[[1]], round(row$y) + search_radius)
  col_indices <- max(1L, round(row$x) - search_radius):min(dim(image)[[2]], round(row$x) + search_radius)
  local <- image[row_indices, col_indices, , drop = FALSE]
  colored <- color_mask(local, "#0000FF") | color_mask(local, "#FFFF00")
  indices <- which(colored, arr.ind = TRUE)
  assert_true(nrow(indices) > 0L, "No blue/yellow C00022 pixels were found near the KGML center")

  global_rows <- row_indices[[1]] - 1L + indices[, "row"]
  global_cols <- col_indices[[1]] - 1L + indices[, "col"]
  bbox <- list(
    left = min(global_cols),
    right = max(global_cols),
    top = min(global_rows),
    bottom = max(global_rows)
  )
  observed_center <- c(x = mean(c(bbox$left, bbox$right)), y = mean(c(bbox$top, bbox$bottom)))
  expected_center <- c(x = row$x, y = row$y)
  mirrored_y <- dim(image)[[1]] - expected_center[["y"]]
  assert_true(abs(observed_center[["x"]] - expected_center[["x"]]) <= 2, "Compound x center shifted")
  assert_true(abs(observed_center[["y"]] - expected_center[["y"]]) <= 2, "Compound y center shifted or vertically mirrored")

  observed_half_width <- max(abs(c(bbox$left, bbox$right) - expected_center[["x"]]))
  observed_half_height <- max(abs(c(bbox$top, bbox$bottom) - expected_center[["y"]]))
  gene_cpd_geometry <<- list(
    compound = "C00022",
    image_height = dim(image)[[1]],
    kgml_center = as.list(expected_center),
    observed_colored_center = as.list(observed_center),
    vertically_mirrored_candidate_y = unname(mirrored_y),
    colored_bbox = bbox,
    observed_half_width_px = unname(observed_half_width),
    observed_half_height_px = unname(observed_half_height),
    kgml_width_px = row$width,
    kgml_height_px = row$height,
    kgml_radius_if_dimensions_are_diameters_px = min(row$width, row$height) / 2
  )
  gene_cpd_geometry
})

# This comparison check keeps the measured R result even when
# it differs from the v3 interpretation. Pathview Plus v3 treats KGML compound
# width/height as a diameter; this installed R pathview renderer uses width as
# the circle radius in its native drawing loop.
if (is.null(gene_cpd_geometry)) {
  record_check(
    "compound size matches KGML diameter convention used by Pathview Plus v3",
    "fail",
    error = "Compound geometry was unavailable because the preceding check failed"
  )
} else {
  expected_radius <- gene_cpd_geometry$kgml_radius_if_dimensions_are_diameters_px
  observed_radius <- max(
    gene_cpd_geometry$observed_half_width_px,
    gene_cpd_geometry$observed_half_height_px
  )
  matches <- abs(observed_radius - expected_radius) <= 1
  record_check(
    "compound size matches KGML diameter convention used by Pathview Plus v3",
    if (matches) "pass" else "fail",
    details = c(
      gene_cpd_geometry,
      list(
        comparison = "Pathview Plus v3 uses min(width, height) / 2 as compound radius",
        expected_radius_px = expected_radius,
        observed_radius_px = observed_radius,
        tolerance_px = 1
      )
    ),
    error = if (matches) NULL else paste0(
      "R pathview observed radius ", observed_radius,
      " px; the KGML-diameter/v3 expectation is ", expected_radius, " px"
    )
  )
}

geometry_output <- file.path(out, "compound-geometry.json")
jsonlite::write_json(
  list(
    method = "Measured blue/yellow pixels around C00022 on a locally generated blank background",
    result = gene_cpd_geometry
  ),
  geometry_output,
  pretty = TRUE,
  auto_unbox = TRUE,
  null = "null"
)

statuses <- vapply(report$checks, `[[`, character(1), "status")
report$summary <- list(
  total = length(statuses),
  passed = sum(statuses == "pass"),
  failed = sum(statuses == "fail"),
  skipped = sum(statuses == "skipped"),
  interpretation = paste(
    "A failed comparison check records a reproducible difference;",
    "it does not by itself mean the R package crashed."
  )
)

json_output <- file.path(out, "comparison.json")
jsonlite::write_json(report, json_output, pretty = TRUE, auto_unbox = TRUE, null = "null")

check_rows <- lapply(report$checks, function(item) {
  data.frame(
    id = item$id,
    name = item$name,
    status = item$status,
    seconds = item$seconds,
    error = if (is.null(item$error)) "" else item$error,
    details_json = if (is.null(item$details)) "" else jsonlite::toJSON(item$details, auto_unbox = TRUE, null = "null"),
    stringsAsFactors = FALSE
  )
})
csv_output <- file.path(out, "check-results.csv")
utils::write.csv(do.call(rbind, check_rows), csv_output, row.names = FALSE)

cat("\nWrote ", json_output, "\n", sep = "")
cat("Wrote ", csv_output, "\n", sep = "")
cat(
  "R pathview comparison: ", report$summary$passed, " passed, ",
  report$summary$failed, " failed, ", report$summary$skipped, " skipped\n",
  sep = ""
)
