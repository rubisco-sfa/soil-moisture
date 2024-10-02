#!/bin/bash -l
#SBATCH --job-name=ilambsm
#SBATCH --account=cli137
#SBATCH --time=6:00:00
#SBATCH --nodes=4
#SBATCH --output=%x.log

bash
module unload darshan-runtime
conda activate /ccs/proj/cli137/nate/ilamb272

export PYTHONPATH=$PYTHONPATH:.
export ILAMB_ROOT=/lustre/orion/cli137/proj-shared/soil_moisture
cd $SLURM_SUBMIT_DIR

srun -n 16 --cpu-bind=cores --distribution=cyclic ilamb-run \
     --config soil_moisture.cfg \
     --model_setup models.yaml \
     --title "CMIP6 Soil Moisture" \
     --define_regions ${ILAMB_ROOT}/data/regions/GlobalLandNoAnt.nc ${ILAMB_ROOT}/data/regions/Koppen.nc \
     --regions global tropical arid temperate cold polar \
     --build_dir ./_build \
     --rmse_score_basis cycle \
