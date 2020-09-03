import os
from process_physio_and_run_retroicor import *
import glob

os.system('mkdir /danl/Collaborations/studyforrest/motion_retroicor')

#subs = glob.glob('/danl/Collaborations/studyforrest/bids_raw/sub-*')
#subs = ['sub-20', 'sub-03', 'sub-04']
#subs = ['sub-06', 'sub-09', 'sub-10', 'sub-14']
subs = ['sub-15', 'sub-17', 'sub-18', 'sub-19']


for sub in subs:
	subid = sub.split('/')[-1]
	print(subid)
	for run in [1,2,3,4,5,6,7,8]:
		physio_path = f'/danl/Collaborations/studyforrest/bids_raw/{subid}/ses-movie/func/{subid}_ses-movie_task-movie_run-{str(run)}_recording-cardresp_physio.tsv.gz'
		nifti_path = f'/danl/Collaborations/studyforrest/bids_raw/{subid}/ses-movie/func/{subid}_ses-movie_task-movie_run-{str(run)}_bold.nii.gz'
		output_dir = f'/danl/Collaborations/studyforrest/bids_raw/{str(subid)}/ses-movie/func/'
		print(physio_path)
		print(nifti_path)
		print(output_dir)
		
		run_r(nifti_image = nifti_path, physio_path = physio_path, output_dir = output_dir, fs = 500.0)

		# 3dvolreg no retroicor
		os.system(f'3dvolreg -1Dfile /danl/Collaborations/studyforrest/motion_retroicor/motion_{subid}_run_{run}.1D {nifti_path}')
		os.system('rm volreg*')

		# 3dvolreg retroicor 
		os.system(f'3dvolreg -1Dfile /danl/Collaborations/studyforrest/motion_retroicor/motion_{subid}_run_{run}_retroicor.1D {output_dir}/{subid}_ses-movie_task-movie_run-{str(run)}_bold_retroicor.nii.gz')
		os.system('rm volreg*')