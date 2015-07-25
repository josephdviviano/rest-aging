#!/usr/bin/env python

import os, sys
import csv
import fnmatch

import numpy as np
import scipy as sp
import nibabel as nib

def TR_drop(directory, func_name, u_id, num, head_mm=50, FD=0.3, DV=0.3):
    """
    Removes motion-corrupted TRs from data, without interpolation. If called
    from the command line, this will batch process all runs in all sessions 
    for a given subject.

    func__pre = functional data prefix (e.g., 'func_filtered')
    mask_name = mask file name (e.g., 'anat_EPI_mask')
    u_id      = unique identifier
    num       = run number
    head_mm   = head radius in mm (default 50 mm)
    FD        = censor TRs with instantaneous motion > x mm (default 0.3 mm)
    DV        = censor TRs with instantaneous GS fluctuation > x % (def. 0.3 %)

    Defaults taken from Gwig et al. 2013 Cerebral Ctx and are subject to
    change.

    """

    print('')
    print(' TR_drop: ' + str(func_name) + '.' + str(u_id) + '.' + str(num))
    print('             FD = ' + str(thresh_FD) + ' mm,')
    print('          DVARS = ' + str(thresh_DV) + ' %,')
    print('    Head Radius = ' + str(head_size) + ' mm.')
    print('')

    # convert/confirm variable types
    directory = str(directory)
    func_name = str(func_name)
    num = str(num)
    head_mm = float(head_mm)
    FD = float(thresh_FD)
    DV = float(thresh_DV)

    # open up a csv
    f = open(directory + '/PARAMS/retained_TRs.' + str(u_id) + '.' + 
                                                   str(num) + '.1D', 'wb')

    # load data, affine, header, get image dimensions
    data = nib.load(os.path.join(directory, func_name))
    outA = data.get_affine()
    outH = data.get_header()
    dims = np.array(data.shape)
    data = data.get_data()

    # reshape to 2D
    data = np.reshape(data, (dims[0] * dims[1] * dims[2], dims[3]))

    # load motion parameters
    for fname in os.listdir(os.path.join(directory, 'PARAMS')):
        if fnmatch.fnmatch(fname, 'motion.' + str(u_id) + '.' + str(num) + '*'):
            FD = np.genfromtxt(os.path.join(directory, 'PARAMS', fname))

            FD[:,0] = np.radians(FD[:,0])*head_size # roll
            FD[:,1] = np.radians(FD[:,1])*head_size # pitch
            FD[:,2] = np.radians(FD[:,2])*head_size # yaw

            # sum over absolute derivative for the 6 motion parameters
            FD = np.sum(np.abs(np.diff(FD, n=1, axis=0)), axis=1)
            FD = np.insert(FD, 0, 0) # align FD & DVARS

        if fnmatch.fnmatch(fname, 'DVARS.' + str(u_id) + '.' + str(num) + '*'):
            DV = np.genfromtxt(os.path.join(directory, 'PARAMS', fname))
            DV = (DV) / 1000 # convert to % signal change
    
    # mask TRs 2 back and 2 forward from threshold
    idx_FD = np.where(FD >= thresh_FD)[0]
    idx_DV = np.where(DV >= thresh_DV)[0] 
    idx = np.union1d(idx_FD, idx_DV)
    idx = np.union1d(
          np.union1d(
          np.union1d(
          np.union1d(idx-2, idx-1), idx), idx+1), idx+2)

    # remove censor idx < 0 and > length of run
    idx = idx[idx > 0]
    idx = idx[idx < dims[3]]
    
    # find all the kosher TRs
    idx_retained = np.setdiff1d(np.arange(dims[3]), idx)

    # 'scrub' the data
    data = data[:, idx_retained]

    # keep track of the number of retained TRs
    dims[3] = len(idx_retained)
    print('Retained ' + str(dims[3]) + 'TRs: run ' + str(num))

    # reshape data, header
    outH.set_data_shape((dims[0], dims[1], dims[2], dims[3]))
    data = np.reshape(data, (dims[0], dims[1], dims[2], dims[3]))
    
    # write 4D output
    data = nib.nifti1.Nifti1Image(data, outA, outH)
    data.to_filename(os.path.join(directory, 'func_scrubbed.' +
                                    str(u_id) + '.' + str(num) + '.nii.gz'))

    # write out number of retained TRs
    f.write(str(dims[3]))
    f.close()

if __name__ == "__main__":
    TR_drop(sys.argv[1], sys.argv[2], sys.argv[3],
            sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
