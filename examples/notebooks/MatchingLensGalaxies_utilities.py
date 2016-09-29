import numpy as np
from matplotlib import pyplot as plt
# from astroML.plotting.tools import draw_ellipse
from astroML.plotting import setup_text_plots
# from sklearn.mixture import GMM as skl_GMM

def plot_bic(param_range,bics,lowest_comp):
    plt.clf()
    setup_text_plots(fontsize=16, usetex=True)
    fig = plt.figure(figsize=(12, 6))
    plt.plot(param_range,bics,color='blue',lw=2, marker='o')
    plt.text(lowest_comp, bics.min() * 0.97 + .03 * bics.max(), '*',
             fontsize=14, ha='center')

    plt.xticks(param_range)
    plt.ylim(bics.min() - 0.05 * (bics.max() - bics.min()),
             bics.max() + 0.05 * (bics.max() - bics.min()))
    plt.xlim(param_range.min() - 1, param_range.max() + 1)

    plt.xticks(param_range,fontsize=14)
    plt.yticks(fontsize=14)

    plt.xlabel('Number of components',fontsize=18)
    plt.ylabel('BIC score',fontsize=18)

    plt.show()

def get_demo_data(flist):
    x0 = np.array([])
    x0_err = np.array([])
    x1 = np.array([])
    x1_err = np.array([])
    c = np.array([])
    c_err = np.array([])
    z = np.array([])
    z_err = np.array([])
    logr = np.array([])
    logr_err = np.array([])
    umag = np.array([])
    umag_err = np.array([])
    gmag = np.array([])
    gmag_err = np.array([])
    rmag = np.array([])
    rmag_err = np.array([])
    imag = np.array([])
    imag_err = np.array([])
    zmag = np.array([])
    zmag_err = np.array([])
    SB_u = np.array([])
    SB_u_err = np.array([])
    SB_g = np.array([])
    SB_g_err = np.array([])
    SB_r = np.array([])
    SB_r_err = np.array([])
    SB_i = np.array([])
    SB_i_err = np.array([])
    SB_z = np.array([])
    SB_z_err = np.array([])

    profile = np.array([]) #29
    urad = np.array([])
    urad_err = np.array([])
    grad = np.array([])
    grad_err = np.array([])
    rrad = np.array([])
    rrad_err = np.array([])
    irad = np.array([])
    irad_err = np.array([])
    zrad = np.array([])
    zrad_err = np.array([])

    for filename in flist:
        infile = open(filename,'r')
        inlines = infile.readlines()
        infile.close()

        for line1 in inlines:
            if line1[0] == '#': continue
            line = line1.split(',')
            if line[33] == 'nan' \
            or line[39] == 'nan' \
            or line[45] == 'nan' \
            or line[51] == 'nan' \
            or line[57] == 'nan': continue

            # SN params
            x0 = np.append(x0,float(line[7])) #x0
            x0_err = np.append(x0_err, float(line[8]))
            x1 = np.append(x1, float(line[9]))  # x1
            x1_err = np.append(x1_err, float(line[10]))
            c = np.append(c, float(line[11]))  # c
            c_err = np.append(c_err, float(line[12]))

            # Host params
            z = np.append(z, float(line[4]))
            z_err = np.append(z_err, 0.0)
            logr = np.append(logr,np.log10(float(line[15])/float(line[42]))) # r
            logr_err = np.append(logr_err, float(line[43]) / (float(line[42]) * np.log(10)))
            umag = np.append(umag, float(line[18]))  # u_mag
            umag_err = np.append(umag_err, float(line[19]))
            gmag = np.append(gmag, float(line[20]))  # g_mag
            gmag_err = np.append(gmag_err, float(line[21]))
            rmag = np.append(rmag, float(line[22]))  # r_mag
            rmag_err = np.append(rmag_err, float(line[23]))
            imag = np.append(imag, float(line[24]))  # i_mag
            imag_err = np.append(imag_err, float(line[25]))
            zmag = np.append(zmag, float(line[26]))  # z_mag
            zmag_err = np.append(zmag_err, float(line[27]))
            SB_u = np.append(SB_u, float(line[32]))  # SB_u
            SB_u_err = np.append(SB_u_err, float(line[33]))
            SB_g = np.append(SB_g, float(line[38]))  # SB_g
            SB_g_err = np.append(SB_g_err, float(line[39]))
            SB_r = np.append(SB_r, float(line[44]))  # SB_r
            SB_r_err = np.append(SB_r_err, float(line[45]))
            SB_i = np.append(SB_i, float(line[50]))  # SB_i
            SB_i_err = np.append(SB_i_err, float(line[52]))
            SB_z = np.append(SB_z, float(line[56]))  # SB_z
            SB_z_err = np.append(SB_z_err, float(line[57]))

            # Radius params
            if line[29]=='Exp': profile=np.append(profile,1)
            elif line[29]=='deV': profile=np.append(profile,4)
            urad = np.append(urad, float(line[30]))
            urad_err = np.append(urad_err, float(line[31]))
            grad = np.append(grad, float(line[36]))
            grad_err = np.append(grad_err, float(line[37]))
            rrad = np.append(rrad, float(line[42]))
            rrad_err = np.append(rrad_err, float(line[43]))
            irad = np.append(irad, float(line[48]))
            irad_err = np.append(irad_err, float(line[49]))
            zrad = np.append(zrad, float(line[54]))
            zrad_err = np.append(zrad_err, float(line[55]))

    ug = umag-gmag
    ug_err = np.sqrt(umag_err**2+gmag_err**2)
    ur = umag-rmag
    ur_err = np.sqrt(umag_err**2+rmag_err**2)
    ui = umag-imag
    ui_err = np.sqrt(umag_err**2+imag_err**2)
    uz = umag-zmag
    uz_err = np.sqrt(umag_err**2+zmag_err**2)
    gr = gmag-rmag
    gr_err = np.sqrt(gmag_err**2+rmag_err**2)
    gi = gmag-imag
    gi_err = np.sqrt(gmag_err**2+imag_err**2)
    gz = gmag-zmag
    gz_err = np.sqrt(gmag_err**2+zmag_err**2)
    ri = rmag-imag
    ri_err = np.sqrt(rmag_err**2+imag_err**2)
    rz = rmag-zmag
    rz_err = np.sqrt(rmag_err**2+zmag_err**2)
    iz = imag-zmag
    iz_err = np.sqrt(imag_err**2+zmag_err**2)

    X = np.vstack([x0, x1, c, z, logr, ug, ur, ui, uz, gr, gi, gz, ri, 
                   rz, iz, SB_u, SB_g, SB_r, SB_i, SB_z]).T
    #X = np.vstack([x0, x1, c, z, logr, ug, ur, ui, uz, gr, gi, gz, ri, rz, iz]).T
    Xerr = np.zeros(X.shape + X.shape[-1:])
    diag = np.arange(X.shape[-1])
    
    Xerr[:,  diag,  diag] = np.vstack([x0_err**2, x1_err**2, c_err**2,
                                     z_err**2, logr_err**2, ug_err**2,
                                     ur_err**2, ui_err**2, uz_err**2,
                                     gr_err**2, gi_err**2, gz_err**2,
                                     ri_err**2, rz_err**2, iz_err**2,
                                     SB_u_err**2, SB_g_err**2,
                                     SB_r_err**2, SB_i_err**2,
                                     SB_z_err**2]).T
    '''
    Xerr[:,  diag,  diag] = np.vstack([x0_err**2, x1_err**2, c_err**2,
                                     z_err**2, logr_err**2, ug_err**2,
                                     ur_err**2, ui_err**2, uz_err**2,
                                     gr_err**2, gi_err**2, gz_err**2,
                                     ri_err**2, rz_err**2, iz_err**2]).T
    '''
    rad_params = np.vstack([profile, umag, umag_err, urad, urad_err, gmag,
                            gmag_err, grad, grad_err, rmag, rmag_err, rrad,
                            rrad_err, imag, imag_err, irad, irad_err, zmag,
                            zmag_err, zrad, zrad_err]).T
    return X, Xerr, rad_params

def plot_separation(test_R, sample_R):
    plt.clf()
    setup_text_plots(fontsize = 16, usetex = True)
    fig = plt.figure(figsize = (12,8))

    plt.hist(test_R, 50, histtype = 'step', color = 'red', lw = 2,
             label = 'Test', range = (-2.5,2.5))
    plt.hist(sample_R, 50, histtype = 'step', color = 'blue',lw = 2,
             label = 'Sample', range = (-2.5,2.5))

    plt.legend(loc="best")
    plt.xlabel("$\log(R/R_e)$", fontsize=18)
    plt.ylabel("Number", fontsize=18)
    plt.xlim(-2.5, 2.5)
    plt.show()

def get_local_SB(R_params, sample_logR):
    SB = []
    SB_err = []

    for i in range(len(sample_logR)):
        sep = (10**(sample_logR[i])) * float(R_params[i][11]) #separation

        SBs = np.array([])
        SB_errs = np.array([])

        for j in range(5):
            halfmag = float(R_params[i][j*4+1]) + 0.75257
            magerr = float(R_params[i][j*4+2])
            Re = float(R_params[i][j*4+3])
            Re_err = float(R_params[i][j*4+4])
            r = sep/Re

            Ie = halfmag + 2.5 * np.log10(np.pi * Re**2)
            Re2_unc = 2 * Re * Re_err * np.pi
            log_unc = 2.5 * Re2_unc / (np.log10(np.pi * Re**2) * np.log(10))
            Ie_unc = np.sqrt(magerr**2 + log_unc**2)

            if R_params[i][0] == 'Exp':
                Io = Ie-1.824
                Io_unc = Ie_unc
                sb = Io*np.exp(-1.68*(r))
                exp_unc = np.exp(-1.68*(r))*1.68*sep*Re_err/(Re**2)
                sb_unc = sb * np.sqrt((Io_unc/Io)**2 +
                                      (exp_unc/np.exp(-1.68*(r)))**2)
                if np.isnan(sb_unc): sb_unc = 0.0
                if sb_unc < 0: sb_unc = sb_unc*-1.0
                SBs = np.append(SBs,sb)
                SB_errs = np.append(SB_errs,sb_unc)

            if R_params[i][0] == 'deV':
                Io = Ie-8.328
                Io_unc = Ie_unc
                sb = Io*np.exp(-7.67*((r)**0.25))
                exp_unc = np.exp(-7.67*((r)**0.25))*7.67*sep*Re_err/(4*Re**(1.25))
                sb_unc = sb*np.sqrt((Io_unc/Io)**2+(exp_unc \
                       /np.exp(-7.67*((r)**0.25))))
                if np.isnan(sb_unc): sb_unc = 0.0
                if sb_unc < 0: sb_unc = sb_unc*-1.0
                SBs = np.append(SBs,sb)
                SB_errs = np.append(SB_errs,sb_unc)

        SB.append(SBs)
        SB_err.append(SB_errs)

    SB = np.array(SB)
    SB_err = np.array(SB_err)
    return SB, SB_err
