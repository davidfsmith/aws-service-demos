from PIL import Image, ImageDraw
import sys
import json
import boto3

fileName = args.fileName

def rekFaceDetection(bucketName, fileName):

    rek = boto3.client('rekognition')

    response = rek.detect_faces(
        Image={
            'S3Object': {
            'Bucket': bucketName,
            'Name': keyName,
        }
        },
        Attributes=[
            'DEFAULT',
        ]
    )
    return response

faceObj = rekFaceDetection(fileName)

def getObject(bucketName, fileName):

    os.chdir('/tmp')
    s3 = boto3.resource('s3')
    s3.meta.client.download_file(bucketName, fileName, fileName)

def uploadObject(bucketName, fileName):

    os.chdir('/tmp')
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('rek-' + fileName, bucketName, 'rek-' + fileName)

def processImage(fileName):
    os.chdir('/tmp')
    im = Image.open(fileName)

    draw = ImageDraw.Draw(im)

    # Convert fractional bounding box coordinates from recognition and convert to absolute pixals
    def computeRectangleCoordinates(image, face):
        # Extract fractional values
        left   = face['BoundingBox']['Left']
        top    = face['BoundingBox']['Top']
        width  = face['BoundingBox']['Width']
        height = face['BoundingBox']['Height']
        # Convert fractional values to pixel values
        x0 = (int)(image.width*left)
        y0 = (int)(image.height*top)
        x1 = (int)(x0 + image.width*width)
        y1 = (int)(y0 + image.height*height)
        return [x0, y0, x1, y1]


    # Get face bounding box cordinates from rek reponse and iterate over them to draw boxes on image
    for faceCords in faceObj['FaceDetails']:
        coOrds = computeRectangleCoordinates(im, faceCords)
        coOrds1 = [x+1 for x in coOrds]
        coOrds2 = [x+2 for x in coOrds]
        coOrds3 = [x+3 for x in coOrds]
        draw.rectangle(coOrds, outline="blue")
        draw.rectangle(coOrds1, outline="white")
        draw.rectangle(coOrds2, outline="white")
        draw.rectangle(coOrds3, outline="blue")

    del draw

    # write to stdout
    im.save('rek-' + newFileName)

def lambda_handler(event, context):
    bucketName = event['records'][0]['s3']['bucket']['name']
    fileName = event['records'][0]['s3']['object']['key']
    getObject(bucketName, fileName)
    processImage(fileName)
    uploadObject(bucketName, fileName)
    return 'Complete'
