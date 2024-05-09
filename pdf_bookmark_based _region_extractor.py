import PyPDF2
import os
import argparse
from tqdm import tqdm
import argparse



def scale_coords(scale_factor,left,bottom,right,top):
    width = float(right - left)
    height = float(top - bottom)
    
    # Calculate the center of the bounding box
    center_x = float(left + right) / 2
    center_y = float(bottom + top) / 2
    
    # Calculate the new width and height based on the scaling factor
    new_width = float(width * scale_factor)
    new_height = float(height * scale_factor)
    
    # Calculate the new coordinates of the bounding box
    new_left = center_x - new_width / 2
    new_bottom = center_y - new_height / 2
    new_right = center_x + new_width / 2
    new_top = center_y + new_height / 2

    return new_left,new_bottom,new_right,new_top


def getDestinationcoords(Scale_factor,outline):
    
    result = {}
    heading = None
    for obj in outline:
        
        for pg in obj:
            keys_values = {}
            if isinstance(pg, list):
                for key in pg:
                    new_left,new_bottom,new_right,new_top= scale_coords(Scale_factor,key['/Left'], key['/Bottom'],key['/Right'], key['/Top'])
                    coords=[new_left,new_bottom,new_right,new_top]
                    keys_values[key['/Title']] = coords
                result[heading] = keys_values
            else:
                heading = pg['/Title']
    return result


def crop_pdf_page(input_pdf, out_dir, Title,bbox):
    with open(input_pdf, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        # Iterate through each page
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            media_box = page.mediabox

            # Set the cropping box for the page
            page.cropbox.lower_left = (bbox[0], bbox[1])
            # print([bbox[0]+100, bbox[1],bbox[2]+100, bbox[3]])
            page.cropbox.upper_right = (bbox[2], bbox[3])

            # Add the cropped page to the output PDF
            writer.add_page(page)

        # Write the output PDF to a file
        with open(out_dir+"/"+Title+".pdf", 'wb') as output_file:
            writer.write(output_file)


def main(scale_factor,input_pdf_dir, output_dir):


    pdf_list = os.listdir(input_pdf_dir)

    for file_name in tqdm(pdf_list):

        sourcePDFFile = os.path.join(input_pdf_dir,file_name)
        while not os.path.exists(sourcePDFFile):
            print('Source PDF not found, sleeping...')
            exit(0)
            
        if os.path.exists(sourcePDFFile):
            #Process file
            pdfFileObj2 = open(sourcePDFFile, 'rb')
            pdfReader = PyPDF2.PdfReader(pdfFileObj2)
            results = getDestinationcoords(scale_factor,pdfReader.outline)
            parent_directory = os.path.join(output_dir,file_name.split("/")[-1])
            os.makedirs(parent_directory, exist_ok=True)
            for Title, sub_dict in results.items():
                os.makedirs(os.path.join(parent_directory,Title), exist_ok=True)
                for sub_title, bbox in sub_dict.items():
                    pth = os.path.join(parent_directory,Title)
                    # os.makedirs(pth, exist_ok=True)
                    crop_pdf_page(sourcePDFFile, pth, sub_title, bbox)    
        else: 
            print("File not found")       


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process command line arguments")
    parser.add_argument("-s", "--scale_factor", type=float, required=True, help="Scale factor")
    parser.add_argument("-i", "--input_pdf_dir", type=str, required=True, help="Input PDF directory")
    parser.add_argument("-o", "--output_dir", type=str, required=True, help="Output directory")
    
    args = parser.parse_args()
    
    main(args.scale_factor, args.input_pdf_dir, args.output_dir)
