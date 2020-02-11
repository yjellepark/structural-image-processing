import os,sys, shutil
import numpy as np

combined_template = '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/combined/combined_template.nii.gz'
group_template = '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/Younger/Younger_template.nii.gz'

study_dir = '/study3/devfracs/DevFracs_DTI_processing/'
processingCode_dir = study_dir + 'ProcessingCode/'
processedDataDirectory = study_dir + 'Yr2/'   #if it is Year1, Yr1_TBSS

input = sys.argv[1:]
subject_num = input[0]
subject_id = str(int(input[0])+2000)  #if it is Year1, +1000

subj_proc_path = processedDataDirectory + 'DF' + subject_id + '/'
template_registration_dir = subj_proc_path + 'TemplateRegistrationYr2/'
norm_data_dir = subj_proc_path + 'NormalizedDataYr2/'

if not os.path.exists(norm_data_dir):
    os.makedirs(norm_data_dir)

if not os.path.exists(template_registration_dir):
    os.makedirs(template_registration_dir)



#Combine registration with warps to the combined template space:

dwi_to_groupTemp_affine= '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/'+subject_id+'/sub' +subject_num+ '_' + subject_id + '_FAAffine.txt'
dwi_to_groupTemp_warp= '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/'+subject_id+'/sub' +subject_num+ '_' + subject_id +'_FAWarp.nii.gz'
dwi_to_groupTemp_inv_warp= '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/'+subject_id+'/sub' +subject_num+ '_' + subject_id +'_FAInverseWarp.nii.gz'

groupTemp_to_classTemp_affine = '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/Younger/Younger_sub' + subject_num+'_templateAffine.txt'
groupTemp_to_classTemp_warp = '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/Younger/Younger_sub' + subject_num+'_templateWarp.nii.gz'
groupTemp_to_classTemp_inv_warp = '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/Younger/Younger_sub' + subject_num+'_templateInverseWarp.nii.gz'

classTemp_to_combined_affine = '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/combined/combined_Younger_templateAffine.txt'
classTemp_to_combined_warp = '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/combined/combined_Younger_templateWarp.nii.gz'
classTemp_to_combined_inv_warp = '/study/devfracs/DevFracs_DTI_processing/LongitudinalData/ants-template/combined/combined_Younger_templateInverseWarp.nii.gz'

combined_warp = template_registration_dir + 'dtCombinedWarp.nii.gz'
command = 'antsApplyTransforms -d 3 -r ' + combined_template + ' -o ['+combined_warp+',1] -t ' + classTemp_to_combined_warp + ' -t ' + classTemp_to_combined_affine +' -t ' + groupTemp_to_classTemp_warp + ' -t ' + groupTemp_to_classTemp_affine +' -t ' + dwi_to_groupTemp_warp + ' -t ' + dwi_to_groupTemp_affine
os.system(command)

combined_inv_warp = template_registration_dir + 'dtCombinedInverseWarp.nii.gz'
command = 'antsApplyTransforms -d 3 -r ' + combined_template + ' -o ['+combined_inv_warp+',1] -t ['+classTemp_to_combined_affine+',1] -t '+classTemp_to_combined_inv_warp+' -t ['+groupTemp_to_classTemp_affine+',1] -t ' +  groupTemp_to_classTemp_warp + ' -t ['+dwi_to_groupTemp_affine+',1] -t '+dwi_to_groupTemp_warp
os.system(command)



#Warp and Reorient the diffusion tensor:
images_to_warp = []
images_to_warp.append(subj_proc_path+'DTI/dti_tensor.nii.gz') #TENSOR
images_to_warp.append(subj_proc_path+'DTI/dti_FA.nii.gz') #FA
images_to_warp.append(subj_proc_path+'DTI/dti_MD.nii.gz') #MD
images_to_warp.append(subj_proc_path+'DTI/dti_RD.nii.gz') #RD
images_to_warp.append(subj_proc_path+'DTI/dti_AD.nii.gz') #AD


output_warp_images = []
output_warp_images.append(norm_data_dir+'dti_TENSOR.nii.gz')
output_warp_images.append(norm_data_dir+'dti_FA.nii.gz')
output_warp_images.append(norm_data_dir+'dti_MD.nii.gz')
output_warp_images.append(norm_data_dir+'dti_RD.nii.gz')
output_warp_images.append(norm_data_dir+'dti_AD.nii.gz')

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


#Reorient the tensor
command = 'ReorientTensorImage 3 ' + norm_data_dir + 'dti_TENSOR.nii.gz ' + norm_data_dir + 'dti_TENSOR_REORIENTED.nii.gz ' + combined_warp
os.system(command)

os.system('rm -rf ' + tmp_img)
