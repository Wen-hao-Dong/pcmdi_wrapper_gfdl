import os
import argparse

parser = argparse.ArgumentParser(description="Generate portrait plot")
parser.add_argument('--descriptor', type=str, required=True, help='Descriptor for the experiment')
parser.add_argument('--outdir', type=str, required=True, help='Output directory for results')
parser.add_argument('--convention', type=str, required=True, help='Convection of model simulation')

args = parser.parse_args()
descriptor = args.descriptor
outdir = args.outdir
convention = args.convention

def generate_html_gallery(output_path, experiment_name):
    # Define the four seasons and four regions
    seasons = ["MAM", "JJA", "SON", "DJF"]
    regions = ["GLOBAL", "NHEX", "SHEX", "TROPICS"]

    # Prepare the HTML file path
    exp_dir = os.path.join(output_path)
    html_filename = os.path.join(exp_dir, "pcmdi_figures_gallery.html")

    # Open the HTML file to write
    with open(html_filename, "w") as file:
        # Write the HTML structure and CSS
        file.write("<html><head><title>PCMDI Figures Gallery</title>\n")
        file.write("<style>\n")
        file.write("/* Basic styling for the modal */\n")
        file.write(".modal {\n")
        file.write("  display: none;\n")
        file.write("  position: fixed;\n")
        file.write("  z-index: 1;\n")
        file.write("  left: 0;\n")
        file.write("  top: 0;\n")
        file.write("  width: 100%;\n")
        file.write("  height: 100%;\n")
        file.write("  overflow: auto;\n")
        file.write("  background-color: rgba(0,0,0,0.8);\n")
        file.write("  padding-top: 60px;\n")
        file.write("}\n")
        file.write(".modal-content {\n")
        file.write("  margin: auto;\n")
        file.write("  display: block;\n")
        file.write("  max-width: 80%;\n")
        file.write("  max-height: 80%;\n")
        file.write("}\n")
        file.write(".close {\n")
        file.write("  position: absolute;\n")
        file.write("  top: 15px;\n")
        file.write("  right: 35px;\n")
        file.write("  color: #fff;\n")
        file.write("  font-size: 40px;\n")
        file.write("  font-weight: bold;\n")
        file.write("  transition: 0.3s;\n")
        file.write("  cursor: pointer;\n")
        file.write("}\n")
        file.write(".close:hover,\n")
        file.write(".close:focus {\n")
        file.write("  color: #bbb;\n")
        file.write("  text-decoration: none;\n")
        file.write("  cursor: pointer;\n")
        file.write("}\n")
        file.write("/* Grid layout for images */\n")
        file.write(".grid-container {\n")
        file.write("  display: grid;\n")
        file.write("  grid-template-columns: repeat(4, 1fr);\n")
        file.write("  gap: 20px;\n")
        file.write("  align-items: flex-end; /* Align items at the bottom of the grid cell */\n")
        file.write("  margin-top: 20px; /* Optional: Add space above the grid container */\n")
        file.write("}\n")
        file.write(".grid-item {\n")
        file.write("  display: flex;\n")
        file.write("  flex-direction: column;\n")
        file.write("  justify-content: flex-end; /* Align the image to the bottom of the cell */\n")
        file.write("  text-align: center;\n")
        file.write("  border: 2px solid #ccc; /* Border around each plot */\n")
        file.write("  padding: 10px; /* Add padding for some space between the image and border */\n")
        file.write("  border-radius: 10px; /* Optional: rounded corners for a smoother look */\n")
        file.write("}\n")
        file.write(".grid-item img {\n")
        file.write("  width: 100%; /* Make the image fill the width of the grid item */\n")
        file.write("  height: auto; /* Maintain aspect ratio based on the width */\n")
        file.write("  border: 1px solid #999; /* Border around each image */\n")
        file.write("  border-radius: 5px; /* Optional: rounded corners for the image itself */\n")
        file.write("}\n")
        file.write("</style>\n")
        file.write("</head><body>\n")

        # Title
        file.write(f"<h1 style='text-align: center;'>PCMDI (v2.2.2) Mean Climate Metrics Figures Gallery for Experiment: {experiment_name}</h1>\n")

        # Start a container for the grid layout
        file.write("<div class='grid-container'>\n")

        # Add the plots for 4 regions over 4 seasons (mean_clim_portrait_plot_4regions_{season}.png)
        for season in seasons:
            image_filename = os.path.join(exp_dir, f"mean_clim_portrait_plot_4regions_{season}_{convention}.png")
            if os.path.exists(image_filename):
                file.write("<div class='grid-item'>\n")
                file.write(f"<img src='{image_filename}' alt='4 Regions over {season}' onclick='openModal(\"{image_filename}\")'/><br/>\n")
                file.write("</div>\n")
            else:
                print(f"Image file {image_filename} not found.")
       
        # Add the plots for 4 seasons over 4 regions (mean_clim_portrait_plot_4seasons_{region}.png)
        for region in regions:
            image_filename = os.path.join(exp_dir, f"mean_clim_portrait_plot_4seasons_{region}_{convention}.png")
            if os.path.exists(image_filename):
                file.write("<div class='grid-item'>\n")
                file.write(f"<img src='{image_filename}' alt='4 Seasons over {region}' onclick='openModal(\"{image_filename}\")'/><br/>\n")
                file.write("</div>\n")
            else:
                print(f"Image file {image_filename} not found.")

        # End the grid container
        file.write("</div>\n")

        # Modal structure for image view
        file.write("<div id='myModal' class='modal'>\n")
        file.write("<span class='close' onclick='closeModal()'>&times;</span>\n")
        file.write("<img class='modal-content' id='modalImage'>\n")
        file.write("</div>\n")

        # JavaScript for modal functionality
        file.write("<script>\n")
        file.write("function openModal(imageSrc) {\n")
        file.write("  var modal = document.getElementById('myModal');\n")
        file.write("  var modalImage = document.getElementById('modalImage');\n")
        file.write("  modal.style.display = 'block';\n")
        file.write("  modalImage.src = imageSrc;\n")
        file.write("}\n")
        file.write("function closeModal() {\n")
        file.write("  var modal = document.getElementById('myModal');\n")
        file.write("  modal.style.display = 'none';\n")
        file.write("}\n")
        file.write("</script>\n")

        # Close HTML tags
        file.write("</body></html>\n")

    print(f"HTML file '{html_filename}' created successfully.")


# Example usage:
output_path = '/home/Wenhao.Dong/internal_html/PCMDI_c96L65_am5f7c1r0_amip'
experiment_name = 'c96L65_am5f7c1r0_amip'  # Replace with your experiment name
generate_html_gallery(outdir, descriptor)
