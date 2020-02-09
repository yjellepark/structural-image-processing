import os,sys, shutil
import numpy as np

combined_template = '/study/devfracs/sMRI/Yr1/Templates/combined/Combined_template.nii.gz'

study_dir = '/study3/devfracs/sMRI/'
processingCode_dir = study_dir + 'processing/'
processedDataDirectory = study_dir + 'Yr1/'

input = sys.argv[1:]
subject_id =  input[0]

subj_proc_path = processedDataDirectory + 'DF' + subject_id + '/'
template_registration_dir = subj_proc_path + 'TemplateRegistration/'
norm_data_dir = subj_proc_path + 'NormalizedData/'

if not os.path.exists(norm_data_dir):
    os.makedirs(norm_data_dir)

if not os.path.exists(template_registration_dir):
    os.makedirs(template_registration_dir)


#Combine registration with warps to the combined template space:
dwi_to_classTemp_affine= '/study/devfracs/sMRI/Yr1/Templates/2ndGraders/2nd_'+subject_id+'Affine.txt'
dwi_to_classTemp_warp= '/study/devfracs/sMRI/Yr1/Templates/2ndGraders/2nd_'+subject_id+'Warp.nii.gz'
dwi_to_classTemp_inv_warp= '/study/devfracs/sMRI/Yr1/Templates/2ndGraders/2nd_'+subject_id+'InverseWarp.nii.gz'

classTemp_to_combined_affine = '/study/devfracs/sMRI/Yr1/Templates/combined/Combined_2nd_templateAffine.txt'
classTemp_to_combined_warp = '/study/devfracs/sMRI/Yr1/Templates/combined/Combined_2nd_templateWarp.nii.gz'
classTemp_to_combined_inv_warp = '/study/devfracs/sMRI/Yr1/Templates/combined/Combined_2nd_templateInverseWarp.nii.gz'

combined_warp = template_registration_dir + 'dtCombinedWarp.nii.gz'
command = 'antsApplyTransforms -d 3 -r ' + combined_template + ' -o [' +combined_warp +',1] -t ' + classTemp_to_combined_warp + ' -t ' + classTemp_to_combined_affine + ' -t ' + dwi_to_classTemp_warp + ' -t ' + dwi_to_classTemp_affine
os.system(command)

combined_inv_warp = template_registration_dir + 'dtCombinedInverseWarp.nii.gz'
command = 'antsApplyTransforms -d 3 -r ' + combined_template + ' -o ['+combined_inv_warp+',1] -t ['+dwi_to_classTemp_affine+',] -t ' +  dwi_to_classTemp_inv_warp + ' -t ['+classTemp_to_combined_affine+',1] -t '+classTemp_to_combined_inv_warp
os.system(command)


#Warp and Reorient the diffusion tensor:
images_to_warp = []
images_to_warp.append(subj_proc_path+ 'DF' + subject_id + '_T1_biasCorrected') #T1 data

output_warp_images = []
output_warp_images.append(norm_data_dir+'sMRI_T1.nii.gz')

tmp_img = norm_data_dir + 'tmp.nii.gz'

for i in range(0, len(images_to_warp)):
    input_img = images_to_warp[i]
    output_img = output_warp_images[i]

    if i == 0:
        command = 'TVAdjustVoxelspace -in ' + input_img + ' -out ' + tmp_img + ' -origin 0 0 0'
    	os.system(command)
    else:
        command = 'SVAdjustVoxelspace -in ' + input_img + ' -out ' + tmp_img + ' -origin 0 0 0'
    	os.system(command)

    command = 'antsApplyTransforms -d 3 '

    if i == 0:
        command += '-e 2 '
    else:
        command += '-e 0 '

    command += '-r ' + combined_template + ' -i ' + tmp_img + ' -o ' + output_img + ' -t ' + combined_warp
    os.system(command)


os.system('rm -rf ' + tmp_img)
