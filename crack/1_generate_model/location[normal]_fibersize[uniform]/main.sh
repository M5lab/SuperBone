#!/bin/bash

# Prompt for starting and ending seed values
read -p "Enter the start fiber seed: " fiber_seed_start
read -p "Enter the end fiber seed: " fiber_seed_end
read -p "Enter the start location seed: " loc_seed_start
read -p "Enter the end location seed: " loc_seed_end

# 確保輸入值為有效的數字
if ! [[ "$fiber_seed_start" =~ ^[0-9]+$ ]] || ! [[ "$fiber_seed_end" =~ ^[0-9]+$ ]] || \
   ! [[ "$loc_seed_start" =~ ^[0-9]+$ ]] || ! [[ "$loc_seed_end" =~ ^[0-9]+$ ]]; then
    echo "Error: All inputs must be valid positive integers."
    exit 1
fi

# 確保範圍正確
if (( fiber_seed_end < fiber_seed_start )) || (( loc_seed_end < loc_seed_start )); then
    echo "Error: End seed values must be greater than or equal to start seed values."
    exit 1
fi

# Loop to execute generate_model.sh
for ((i = 0; i <= (fiber_seed_end - fiber_seed_start); i++)); do
    current_fiber_seed=$((fiber_seed_start + i))
    for ((j = 0; j <= (loc_seed_end - loc_seed_start); j++)); do
        current_loc_seed=$((loc_seed_start + j))
        echo "Executing with fiber_seed = $current_fiber_seed, loc_seed = $current_loc_seed"
        bash ./generate_model.sh "$current_fiber_seed" "$current_loc_seed"
    done
done

echo "All files have been generated!"