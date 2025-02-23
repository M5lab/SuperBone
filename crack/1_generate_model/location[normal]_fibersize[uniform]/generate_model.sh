#!/bin/bash

sw_vers

DATE_FORMAT=$(date +"%Y-%m-%d")
TIME_FORMAT=$(date +"%H:%M:%S")
echo "Today is $DATE_FORMAT and now time is $TIME_FORMAT"
record_txt="${DATE_FORMAT}_run_current.txt"

set -e

# 使用命令行參數接收值
fiber_seed=$1
loc_seed=$2

# 檢查是否提供了參數
if [[ -z "$fiber_seed" || -z "$loc_seed" ]]; then
    echo "Error: Missing fiber_seed or loc_seed. Usage: ./generate_model.sh <fiber_seed> <loc_seed>"
    exit 1
fi

WORKDIR=$(dirname "$0")/code

cd "$WORKDIR"


# 檢查 ../data/1_matrix.data 是否存在
if [ -f "../data/1_matrix.data" ]; then
    echo "File ../data/1_matrix.data already exists. Skipping execution of LAMMPS."
else
    echo "File ../data/1_matrix.data not found. Running LAMMPS with 0_generate_matrix.in..."
    lmp -in 1_generate_matrix.in
fi

echo "Starting the script with fiber_seed=$fiber_seed and loc_seed=$loc_seed..."

echo "Running 0_generate_fiber_location.py..."
python3 0_generate_fiber_location.py --seed1 "$fiber_seed" --seed2 "$loc_seed"

# Combine and trim step
echo "Running 1_combine&trim.py..."
python3 2_combine\&trim.py --seed1 "$fiber_seed" --seed2 "$loc_seed"

# 執行最終模型生成
echo "Preparing and running 2_generate_final_model.in..."
lmp -var SEED1 "$fiber_seed" -var SEED2 "$loc_seed" -in 3_generate_final_model.in 

# 清理文件
rm -f "../data/random_pos[${fiber_seed}][${loc_seed}].dump"

echo "All steps completed successfully!"
DATE_FORMAT=$(date +"%Y-%m-%d")
TIME_FORMAT=$(date +"%H:%M:%S")
echo "Today is $DATE_FORMAT and now time is $TIME_FORMAT"
echo "All done!"