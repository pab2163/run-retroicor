import os
from process_physio_and_run_retroicor import *
import glob

os.system('mkdir /danl/Collaborations/studyforrest/motion_retroicor')

subs = glob.glob('/danl/Collaborations/studyforrest/bids_raw/sub-*')
subs.remove('/danl/Collaborations/studyforrest/bids_raw/sub-01') 


for sub in subs:
    subid = sub.split('/')[-1]
    print(subid)
    for run in [1,2,3,4,5,6,7,8]:
        physio_path = f'/danl/Collaborations/studyforrest/bids_raw/{subid}/ses-movie/func/{subid}_ses-movie_task-movie_run-{str(run)}_recording-cardresp_physio.tsv.gz'
        nifti_path = f'/danl/Collaborations/studyforrest/bids_raw/{subid}/ses-movie/func/{subid}_ses-movie_task-movie_run-{str(run)}_bold.nii.gz'
        output_dir = f'/danl/Collaborations/studyforrest/bids_raw/{str(subid)}/ses-movie/func/'
        retroicor_nifti_path = f'/danl/Collaborations/studyforrest/bids_raw/{subid}/ses-movie/func/{subid}_ses-movie_task-movie_run-{str(run)}_bold_retroicor_filt.nii.gz'
        
        # add proper slice timing info from top-level bids spec
        os.system(f'3drefit -Tslices 0.0000, 0.0571, 0.1143, 0.1714, 0.2286, 0.2857, 0.3429, 0.4000, \
            0.4571, 0.5143, 0.5714, 0.6286, 0.6857, 0.7429, 0.8000, 0.8571, 0.9143, 0.9714, 1.0286, 1.0857, \
            1.1429, 1.2000, 1.2571, 1.3143, 1.3714, 1.4286, 1.4857, 1.5429, 1.6000, 1.6571, 1.7143, 1.7714, \
            1.8286, 1.8857, 1.9429 {nifti_path}')

        # preproc physio data
        processed_physio_path = process_physio(physio_path = physio_path, output_dir = output_dir, fs = 500.0)
        processed_physio_path = Path(processed_physio_path).resolve()
        os.system(f'3dretroicor -prefix {retroicor_nifti_path} -resp {processed_physio_path} {nifti_path}')        

        # 3dvolreg no retroicor
        os.system(f'3dvolreg -1Dfile /danl/Collaborations/studyforrest/motion_retroicor/motion_{subid}_run_{run}.1D {nifti_path}')
        os.system('rm volreg*')


        # 3dvolreg retroicor (filtered)
        os.system(f'3dvolreg -1Dfile /danl/Collaborations/studyforrest/motion_retroicor/motion_{subid}_run_{run}_retroicor_filt.1D {output_dir}/{subid}_ses-movie_task-movie_run-{str(run)}_bold_retroicor_filt.nii.gz')
        os.system('rm volreg*')