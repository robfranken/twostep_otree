# get startingn networks

rm(list=ls())
gc()

#devtools::install_github("JochemTolsma/RsienaTwoStep", build_vignettes=TRUE)

library(RsienaTwoStep)
library(jsonlite)

write_json(ts_net2, "ts_net2.json")
write_json(ts_net1, "ts_net1.json")
