#!/usr/bin/env Rscript

# Execute the current Bioconductor pathview baseline on the same frozen KEGG
# pathway and controlled values used by the Python comparison.

args_all <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args_all, value = TRUE)
script_file <- normalizePath(sub("^--file=", "", script_arg[[1]]))
root <- normalizePath(file.path(dirname(script_file), ".."))
.libPaths(c(file.path(root, ".r-library"), .libPaths()))

suppressPackageStartupMessages(library(pathview))
suppressPackageStartupMessages(library(jsonlite))

out <- file.path(root, "results", "pathview_r")
cache <- file.path(root, "cache", "kegg")
dir.create(out, recursive = TRUE, showWarnings = FALSE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)

for (extension in c("xml", "png")) {
  source_file <- system.file("extdata", paste0("hsa04110.", extension), package = "pathview")
  file.copy(source_file, file.path(cache, basename(source_file)), overwrite = TRUE)
}

old_dir <- setwd(out)
on.exit(setwd(old_dir), add = TRUE)

report <- list(
  component = "R pathview",
  version = as.character(packageVersion("pathview")),
  bioconductor = as.character(BiocManager::version()),
  r_version = R.version.string,
  checks = list()
)

run_check <- function(name, expression) {
  start <- proc.time()[["elapsed"]]
  result <- tryCatch(
    {
      details <- force(expression)
      list(
        name = name,
        status = "pass",
        seconds = round(proc.time()[["elapsed"]] - start, 4),
        details = details
      )
    },
    error = function(error) {
      list(
        name = name,
        status = "fail",
        seconds = round(proc.time()[["elapsed"]] - start, 4),
        error = paste(class(error)[[1]], conditionMessage(error), sep = ": ")
      )
    }
  )
  report$checks[[length(report$checks) + 1]] <<- result
  cat(toupper(result$status), " ", name, if (!is.null(result$error)) paste0(": ", result$error), "\n", sep = "")
  invisible(result)
}

palette <- list(
  limit = list(gene = 2, cpd = 2),
  bins = list(gene = 11, cpd = 11),
  both.dirs = list(gene = TRUE, cpd = TRUE),
  low = list(gene = "#00FF00", cpd = "#0000FF"),
  mid = list(gene = "#BEBEBE", cpd = "#BEBEBE"),
  high = list(gene = "#FF0000", cpd = "#FFFF00")
)

base_arguments <- function() {
  list(
    pathway.id = "04110",
    species = "hsa",
    gene.idtype = "entrez",
    kegg.dir = cache,
    kegg.native = TRUE,
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

run_check("official frozen fixture", {
  info <- file.info(file.path(cache, c("hsa04110.xml", "hsa04110.png")))
  if (any(is.na(info$size)) || any(info$size <= 0)) stop("frozen fixture is incomplete")
  list(
    xml_bytes = unname(info$size[[1]]),
    png_bytes = unname(info$size[[2]]),
    source = "Bioconductor pathview 1.52.0 extdata"
  )
})

run_check("controlled one-condition native PNG", {
  gene_vector <- c("1029" = -2, "7157" = -1.6, "1956" = -1.2)
  arguments <- c(
    list(gene.data = gene_vector, out.suffix = "r_classical", multi.state = TRUE),
    base_arguments()
  )
  result <- do.call(pathview, arguments)
  output <- file.path(out, "hsa04110.r_classical.png")
  if (!file.exists(output) || file.info(output)$size <= 0) stop("one-condition PNG was not written")
  write.csv(result$plot.data.gene, file.path(out, "hsa04110.r_classical.gene_nodes.csv"), row.names = FALSE)
  list(
    output = "results/pathview_r/hsa04110.r_classical.png",
    gene_node_rows = nrow(result$plot.data.gene),
    mapped = sum(!is.na(result$plot.data.gene[, "mol.data"]))
  )
})

run_check("controlled two-condition left/right native PNG", {
  gene_matrix <- matrix(
    c(-2, 2, -1.6, 1.6, -1.2, 1.2),
    nrow = 3,
    byrow = TRUE,
    dimnames = list(c("1029", "7157", "1956"), c("Classical", "Basal"))
  )
  arguments <- c(
    list(gene.data = gene_matrix, out.suffix = "r_half_half", multi.state = TRUE),
    base_arguments()
  )
  result <- do.call(pathview, arguments)
  output <- file.path(out, "hsa04110.r_half_half.multi.png")
  if (!file.exists(output) || file.info(output)$size <= 0) stop("half-and-half PNG was not written")
  write.csv(result$plot.data.gene, file.path(out, "hsa04110.r_half_half.gene_nodes.csv"), row.names = FALSE)
  rows_1029 <- grepl("(^|, )1029($|,)", result$plot.data.gene$all.mapped)
  if (!any(rows_1029)) stop("Entrez 1029 did not map")
  if (!all(result$plot.data.gene[rows_1029, "Classical"] == -2, na.rm = TRUE)) stop("Classical value mismatch")
  if (!all(result$plot.data.gene[rows_1029, "Basal"] == 2, na.rm = TRUE)) stop("Basal value mismatch")
  list(
    output = "results/pathview_r/hsa04110.r_half_half.multi.png",
    gene_node_rows = nrow(result$plot.data.gene),
    mapped_classical = sum(!is.na(result$plot.data.gene[, "Classical"])),
    mapped_basal = sum(!is.na(result$plot.data.gene[, "Basal"])),
    state_order = c("Classical (left)", "Basal (right)")
  )
})

run_check("controlled three-condition native PNG", {
  gene_matrix <- matrix(
    c(-2, 0, 2, 2, -2, 0, 0, 2, -2),
    nrow = 3,
    byrow = TRUE,
    dimnames = list(c("1029", "7157", "1956"), c("Control", "Treatment_A", "Treatment_B"))
  )
  arguments <- c(
    list(gene.data = gene_matrix, out.suffix = "r_three_state", multi.state = TRUE),
    base_arguments()
  )
  result <- do.call(pathview, arguments)
  output <- file.path(out, "hsa04110.r_three_state.multi.png")
  if (!file.exists(output) || file.info(output)$size <= 0) stop("three-condition PNG was not written")
  write.csv(result$plot.data.gene, file.path(out, "hsa04110.r_three_state.gene_nodes.csv"), row.names = FALSE)
  list(
    output = "results/pathview_r/hsa04110.r_three_state.multi.png",
    state_order = c("Control", "Treatment_A", "Treatment_B")
  )
})

run_check("official gse16873 classical example", {
  data(gse16873.d, package = "pathview")
  arguments <- c(
    list(gene.data = gse16873.d[, 1], out.suffix = "r_gse16873", multi.state = TRUE),
    base_arguments()
  )
  result <- do.call(pathview, arguments)
  output <- file.path(out, "hsa04110.r_gse16873.png")
  if (!file.exists(output) || file.info(output)$size <= 0) stop("official example PNG was not written")
  write.csv(result$plot.data.gene, file.path(out, "hsa04110.r_gse16873.gene_nodes.csv"), row.names = FALSE)
  list(
    output = "results/pathview_r/hsa04110.r_gse16873.png",
    input_genes = nrow(gse16873.d),
    mapped_nodes = sum(!is.na(result$plot.data.gene[, "mol.data"]))
  )
})

run_check("Graphviz PDF with two states", {
  gene_matrix <- matrix(
    c(-2, 2, -1.6, 1.6, -1.2, 1.2),
    nrow = 3,
    byrow = TRUE,
    dimnames = list(c("1029", "7157", "1956"), c("Classical", "Basal"))
  )
  arguments <- c(
    list(
      gene.data = gene_matrix,
      out.suffix = "r_graph",
      multi.state = TRUE,
      kegg.native = FALSE,
      pathway.id = "04110",
      species = "hsa",
      gene.idtype = "entrez",
      kegg.dir = cache,
      map.symbol = FALSE,
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
  )
  result <- do.call(pathview, arguments)
  output <- file.path(out, "hsa04110.r_graph.multi.pdf")
  if (!file.exists(output) || file.info(output)$size <= 0) stop("Graphviz PDF was not written")
  list(output = "results/pathview_r/hsa04110.r_graph.multi.pdf", bytes = unname(file.info(output)$size))
})

run_check("exported helper surface", {
  required <- c(
    "download.kegg", "node.info", "node.map", "eg2id", "id2eg",
    "cpdidmap", "mol.sum", "sim.mol.data", "node.color", "pathview",
    "keggview.native", "keggview.graph"
  )
  missing <- required[!vapply(required, exists, logical(1), where = asNamespace("pathview"), inherits = FALSE)]
  if (length(missing) > 0) stop(paste("missing exports:", paste(missing, collapse = ", ")))
  list(required_exports = length(required), missing = missing)
})

json_output <- file.path(out, "validation.json")
write_json(report, json_output, pretty = TRUE, auto_unbox = TRUE, null = "null")
passed <- sum(vapply(report$checks, function(item) item$status == "pass", logical(1)))
failed <- sum(vapply(report$checks, function(item) item$status == "fail", logical(1)))
cat("\nWrote ", json_output, "\n", sep = "")
cat("R pathview checks: ", passed, " passed, ", failed, " failed\n", sep = "")
