#!/usr/bin/env Rscript
# Install Rraven from GitHub

# Install remotes if needed
if (!requireNamespace("remotes", quietly = TRUE)) {
  install.packages("remotes", repos = "https://cloud.r-project.org")
}

# Install Rraven from GitHub
remotes::install_github("maRce10/Rraven")

cat("✅ Rraven installed successfully!\n")
