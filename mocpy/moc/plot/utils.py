import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord

from astropy.wcs.utils import pixel_to_skycoord

import warnings

def build_plotting_moc(moc, wcs):
    # Get the WCS cdelt giving the deg.px^(-1) resolution.
    cdelt = wcs.wcs.cdelt
    # Convert in rad.px^(-1)
    cdelt = np.abs((2*np.pi/360)*cdelt[0])
    # Get the minimum depth such as the resolution of a cell is contained in 1px. 
    depth_res = int(np.floor(np.log2(np.sqrt(np.pi/3)/cdelt)))
    depth_res = max(depth_res, 0)
    # Degrade the moc to that depth for plotting purposes. It is not necessary to plot pixels
    # that we will not see because they are contained in 1px.
    moc_plot = moc
    if moc.max_order > depth_res:
        moc_plot = moc.degrade_to_order(depth_res)

    moc_plot = moc_plot.refine_to_order(min_depth=3)

    # Get the MOC delimiting the FOV polygon
    width_px = int(wcs.wcs.crpix[0]*2.) # Supposing the wcs is centered in the axis
    heigth_px = int(wcs.wcs.crpix[1]*2.)

    # Compute the sky coordinate path delimiting the viewport.
    # It consists of a closed polygon of (4 - 1)*4 = 12 vertices
    x_px = np.linspace(0, width_px, 4)
    y_px = np.linspace(0, heigth_px, 4)

    X, Y = np.meshgrid(x_px, y_px)

    X_px = np.append(X[0, :-1], X[:-1, -1])
    X_px = np.append(X_px, X[-1, 1:][::-1])
    X_px = np.append(X_px, X[:-1, 0])

    Y_px = np.append(Y[0, :-1], Y[:-1, -1])
    Y_px = np.append(Y_px, Y[-1, :-1])
    Y_px = np.append(Y_px, Y[1:, 0][::-1])

    # Disable the output of warnings when encoutering NaNs.
    warnings.filterwarnings("ignore")
    # Inverse projection from pixel coordinate space to the world coordinate space
    viewport = pixel_to_skycoord(X_px, Y_px, wcs)
    # If one coordinate is a NaN we exit the function and do not go further
    ra_deg, dec_deg = viewport.icrs.ra.deg, viewport.icrs.dec.deg
    warnings.filterwarnings("default")

    if np.isnan(ra_deg).any() or np.isnan(dec_deg).any():
        return moc_plot

    center_x_px, center_y_px = wcs.wcs.crpix[0], wcs.wcs.crpix[1]
    inside = pixel_to_skycoord(center_x_px, center_y_px, wcs)

    # Import MOC here to avoid circular imports
    from ..moc import MOC
    # Create a rough MOC (depth=3 is sufficient) from the viewport
    moc_viewport = MOC.from_polygon_skycoord(viewport, max_depth=3)

    # The moc to plot is the INPUT_MOC & MOC_VIEWPORT. For small FOVs this can reduce
    # a lot the time to draw the MOC along with its borders.
    moc_plot = moc_plot.intersection(moc_viewport)
    return moc_plot

