from flask import Flask, render_template, request, redirect
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename

import PIL.Image
import PIL.ExifTags
import os, os.path

app = Flask(__name__)

# dropzone configs
dropzone = Dropzone(app)

app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/jpg'
app.config['DROPZONE_REDIRECT_VIEW'] = 'index'

# upload config
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app) # Set default size limit

# transformed config
CHANGED_FOLDER = os.getcwd() + '/transformed'
app.config['CHANGED_FOLDER'] = CHANGED_FOLDER


# default route
@app.route('/', methods=['GET', 'POST'])
def index():
    file_urls = []
    if request.method == 'POST':
        # get the files
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            # save the file with to uploads folder
            filename = photos.save(
                file,
                name=file.filename    
            )
            # store initial image urls
            file_urls.append(photos.url(filename))
        # Extract EXIF Data Function - Uncomment if you want to view the EXIF data
        #exif_extract("./uploads/img.jpg") 
        # Transform function that applies orientation transformations
        exif_transform()
        return "uploading..."
    return render_template('index.html')

# Prints out the EXIF data on the console 
def exif_extract(image):
    img = PIL.Image.open(image)
    exif_data = img._getexif()
    # format the EXIF data items
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }
    print(exif)

# Apply EXIF Transformations
def exif_transform():
    print('testing')
    # for loop for each picture
    img_list = []
    valid_images = [".jpg",".gif",".png",".tga"]
    for file in os.listdir('./uploads'):
        ext = os.path.splitext(file)[1]
        if ext.lower() not in valid_images:
            continue
        img_list.append(PIL.Image.open(os.path.join('./uploads', file)))
    for i in img_list:
        # i = image
        exifs = dict(i._getexif().items())
        # check for Orientation tag in EXIF
        for orientation in PIL.ExifTags.TAGS.keys():
            if PIL.ExifTags.TAGS[orientation]=='Orientation':
                break
        if exifs[orientation] == 3:
            i = i.rotate(180, expand = True)
        elif exifs[orientation] == 6:
            i = i.rotate(270, expand = True)
        elif exifs[orientation] == 8:
            i = i.rotate(90, expand = True)
        elif exifs[orientation] == 1:
            print("orientation is fine")
        # Saves images into transformed folder
        filename = secure_filename(i.filename)
        i.save(os.path.join(app.config['CHANGED_FOLDER'], filename))

# Fixed Photos Route
@app.route('/transformed', methods=['GET','POST'])
def transformed():
    pic_list = os.listdir('./transformed')
    pic_list = [file for file in pic_list]
    return render_template('transformed.html', pics = pic_list)



if __name__ == '__main__':
    app.run(debug=True)