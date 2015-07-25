#! /bin/bash

#IN_PRE='def_D'
#IN_PRE='def_F'
#IN_PRE='d_attn_C'
#IN_PRE='ATOL_MPFC'
IN_PRE='ATOL_PCC'

#CMD1=`echo '"'group1/*${IN_PRE}.nii.gz[1]'"'`
#CMD2=`echo '"'group2/*${IN_PRE}.nii.gz[1]'"'`

# clean up old results
rm group_analysis_${IN_PRE}.nii.gz 

# group - level maps
3dttest++ \
    -setA "group1/*"${IN_PRE}".nii.gz[1]" \
    -setB "group2/*"${IN_PRE}".nii.gz[1]" \
    -labelA young \
    -labelB old \
    -BminusA \
    -prefix group_analysis_${IN_PRE}.nii.gz \
    -pooled \
    -mask mask_group_MNI.nii.gz

