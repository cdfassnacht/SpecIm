"""

echelle1d.py

A generic set of code to process echelle 1d spectra that are stored as a
collection of 1d spectra.  This code is used by some of the ESI and NIRES
code that are in the keckcode repository

"""

from matplotlib import pyplot as plt
from astropy.io import fits as pf
from astropy.table import Table
from specim import specfuncs as ss

class Ech1d(list):
    """
    A generic set of code to process echelle 1d spectra that are stored as a
    collection of 1d spectra.  This code is used by some of the ESI and NIRES
    code that are in the keckcode repository
    """

    def __init__(self, speclist=None, echfile=None, filelist=None,
                 informat=None, verbose=True):
        """

        Load the data.  This can be accomplished in one of three ways:
          1. by providing a list of Spec1d instances
          2. by providing a single filename, where the file contains the
             full set of single 1d spectra that are associated with a
             single echelle exposure for which the extraction has been done
          3. by providing a filelist, where each file in the list contains
             a single 1d spectrum in one of the approved formats
             (see Spec1d for possible informat values)
             [NOT YET IMPLEMENTED]

        """

        """
        First see if the input spectra are being provided as a list of
        Spec1d objects
        """
        if speclist is not None:
            for spec in speclist:
                if isinstance(spec, ss.Spec1d) is not True:
                    print('')
                    print('With speclist option the list must contain'
                          ' Spec1d instances')
                    print('')
                    raise TypeError
                self.append(spec)

        elif echfile is not None:
            if verbose:
                print('Opening echelle spectrum file: %s' % echfile)
            try:
                hdu = pf.open(echfile)
            except IOError:
                raise IOError
            norder = len(hdu) - 1
            for i in range(1, len(hdu)):
                spec = ss.Spec1d(hdu=hdu[i])
                self.append(spec)

        else:
            print('')
            print('NOTE: filelist option is not implemented for input')
            print('')

    # ------------------------------------------------------------------------

    def plot_all(self, plotmode='single', mode='input', title=None, z=None,
                 showz=True, linetype='strongem', smo=None,
                 verbose=False, **kwargs):
        """

        Plots all the spectra in the echelle data set in a single plot.

        """

        """ Set starting values """
        i = 0
        wmin = 1.e12
        wmax = 0.

        """ Plot the spectra """
        for count, spec in enumerate(self):

            """ Set plot labeling """
            if count == len(spec) - 1:
                if title is None:
                    title = 'Extracted Spectrum'
                showz = True
            else:
                title = False
                showz = False

            """ Plot the spectrum """
            if smo is not None:
                spec.smooth(smo, mode=mode, title=title, verbose=verbose,
                            **kwargs)
            else:
                spec.plot(mode=mode, title=title, **kwargs)

            """ Mark spectral lines if desired """
            if z is not None:
                if smo is not None:
                    usesmooth = True
                else:
                    usesmooth = False
                try:
                    spec.mark_lines(linetype, z, showz=showz, 
                                    usesmooth=usesmooth)
                except NameError:
                    spec.mark_lines('strongem', z, showz=showz, 
                                    usesmooth=usesmooth)

            """ Adjust the plot limits """
            if spec['wav'].min() < wmin:
                wmin = spec['wav'].min()
            if spec['wav'].max() > wmax:
                wmax = spec['wav'].max()
            i += 1

        """ Set final plot limits """
        plt.xlim(wmin, wmax)

    # ------------------------------------------------------------------------

    def save_multi(self, outroot, outformat='multitab'):
        """

        Saves the echelle spectra, contained in separate Spec1d instances
         within this class, to one or more output files. 
        The output options are:
         1. 'multitab' - Writes a single output file, which is a 
                         multiextention fits file.  Each extension contains
                         a fits table ('fitstab' format in the Spec1d lingo)
         2. 'text'     - Produces several output files, one for each order.
                         The files are ascii text files, with columns for,
                         at minimum, wavelength and flux, and possibly also
                         variance and sky

        """

        if outformat == 'multitab':

            """
            Set up the required, essentially empty, primary HDU and the
            HDUList
            """
            phdu = pf.PrimaryHDU()
            hdulist = pf.HDUList(phdu)

            """
            Make a separate HDU for each echelle order and then create a HDUList
            """
            lll = [pf.table_to_hdu(Table(spec)) for spec in self]
            hdulist = pf.HDUList([phdu] + lll)

            """ Save the output """
            outfile = '%s.fits' % outroot
            hdulist.writeto(outfile, overwrite=True)

        else:
            print('')
            print('Not yet implemented yet')
            print('')
