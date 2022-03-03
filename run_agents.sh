#!/bin/bash

# For example:
#>> run_agents.sh 4 ptajman/min_pandl_1000/62qm7dcn
# Launching agent 1.
# nohup wandb agent ptajman/min_pandl_1000/62qm7dcn &
# Launching agent 2.
# nohup wandb agent ptajman/min_pandl_1000/62qm7dcn &
# Launching agent 3.
# nohup wandb agent ptajman/min_pandl_1000/62qm7dcn &
# Launching agent 4.
# nohup wandb agent ptajman/min_pandl_1000/62qm7dcn &

N_AGENTS=$1
TAG=$2

CMD="wandb agent ${TAG}"

for i in $(seq 1 $N_AGENTS); do
  echo "Launching agent ${i}."
  nohup $CMD &
done
