#!/bin/bash
#SBATCH --output=logs/output_%j.log       # Log file
#SBATCH --error=logs/error_%j.log         # Error file
#SBATCH --gres=gpu:A40                    # GPUs required

# Load Conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate 311

cd ~/humanEvaluation   # Replace with the absolute path to your folder

# Display GPU information
nvidia-smi

# Run the Python script with arguments
python run_nvs_batch.py
