library(tidyverse)
# setwd("~/CMU/modelFitExample")

data <- data.table::fread("immediate_test.csv", data.table=FALSE)

post_test <- data.frame("q" = paste0("posttest", 1:16),
                        "shape" = rep(c("rect", "circ", "tria", "trap"), each=2, times=2))

data <- data %>% 
  filter(trial_subtype %in% c("training", "posttest-free-response")) %>%
  mutate(q = regmatches(questions, regexpr('(?<=\\/)(.*)(?=\\.)', questions, perl=T))) %>% 
  left_join(post_test) %>% 
  mutate(shape = ifelse(is.na(shape), tolower(substr(q, 1, 4)), shape)) %>% 
  group_by(prolific_id) %>% 
  arrange(prolific_id, trial_index) 


we_sub <- data %>% 
  filter(trial_subtype == "training",
         participant_condition %in% c("S,WE", "F,WE")) %>% 
  mutate(trial_index = trial_index-1,
         correct = TRUE,
         q = paste0(shape, "_we"),
         question_type = "WE")

rp_sub <- data %>% 
  filter(trial_subtype == "training",
         participant_condition %in% c("S,T", "F,T"),
         !duplicated(shape)) %>% 
  mutate(trial_index = trial_index-1,
         correct = TRUE,
         q = paste0(shape, "_we"),
         question_type = "WE")

data_full <- rbind(data, we_sub, rp_sub) %>% 
  group_by(prolific_id) %>% 
  arrange(prolific_id, trial_index) %>% 
  mutate(q = tolower(q),
         correctness = ifelse(correct, 1, 0),
         q_number = row_number(start_time),
         participant_concepts = substr(participant_condition, 0, 1),
         participant_training = substr(participant_condition, 3, 5),
         correct_skill = paste0(shape, "_", participant_concepts),
         activated_skill = ifelse(correct, paste0(shape, "_", participant_concepts), response)) %>%
  select(trial_type, prolific_id, participant_concepts, participant_training, q_number, trial_subtype, question_type,
         correctness, q, shape, correct_skill, activated_skill)

write_csv(data_full, "immediate_test_clean.csv")
