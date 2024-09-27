#!/bin/bash -l
#SBATCH --job-name=ilambsm
#SBATCH --account=cli137
#SBATCH --time=3:00:00
#SBATCH --nodes=4
#SBATCH --output=%x.log

bash
module unload darshan-runtime
conda activate /ccs/proj/cli137/nate/ilamb272

export ILAMB_ROOT=/lustre/orion/cli137/proj-shared/soil_moisture
cd $SLURM_SUBMIT_DIR

srun -n 16 --cpu-bind=cores --distribution=cyclic ilamb-run \
     --config soil_moisture.cfg \
     --model_setup models.yaml \
     --title "CMIP6 Soil Moisture" \
     --define_regions arctic.txt \
     --regions global arctic \
     --build_dir ./_build \
     --rmse_score_basis cycle \
