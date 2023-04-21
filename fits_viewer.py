import streamlit as st
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from skimage import exposure

# Create a title and a brief description
st.title("FITS File Viewer")
st.markdown("Upload a FITS file to display its image and adjust its contrast.")

# Create a file uploader widget
uploaded_file = st.file_uploader("Choose a FITS file", type=["fits"])

# Function to read and plot the FITS file
def plot_fits(file, contrast):
    with fits.open(file) as hdul:
        data = hdul[0].data

        # Apply contrast scaling
        p_low, p_high = np.percentile(data, [contrast, 100 - contrast])
        img_rescale = exposure.rescale_intensity(data, in_range=(p_low, p_high))

        # Create a plot
        fig, ax = plt.subplots()
        ax.imshow(img_rescale, cmap="gray", origin="lower")
        ax.set_title("FITS Image")
        plt.tight_layout()

        # Display the plot
        st.pyplot(fig)

# Check if a file is uploaded
if uploaded_file is not None:
    # Create a slider for contrast adjustment
    contrast = st.slider("Adjust contrast", 0, 100, 2, 1)

    # Plot the image with the selected contrast
    plot_fits(uploaded_file, contrast)

