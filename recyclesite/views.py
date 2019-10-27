from django.shortcuts import render, redirect
from .forms import PostForm
from .models import Post
from django.shortcuts import get_object_or_404
import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from django.db.models import Count

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'recyclesite/static/ODkey.json'

# Create your views here.
def index(request):
    fieldname = 'category'
    group = Post.objects.values(fieldname).order_by(fieldname).annotate(count=Count(fieldname))
    if request.method=="POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit = False)
            post.save()
            return redirect('detail',pk = post.pk)

    else:
        form = PostForm()

    return render(request, 'index.html',{'form':form, 'group':group})


def new(request):
    if request.method=="POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit = False)
            post.save()
            return redirect('detail',pk = post.pk)
    else:
        form = PostForm()

    return render(request, 'index.html',{'form':form})

def detail(request, pk):
    fieldname = 'category'
    group = Post.objects.values(fieldname).order_by(fieldname).annotate(count=Count(fieldname))
    post = get_object_or_404(Post, pk=pk)
    

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = post.image.path

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)
    
    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations
    labelL=[]

    print('Labels:')
    for label in labels:
        print(label.description)
        labelL.append(label.description)
    
    labelstr = (','.join(labelL)).lower()
    
    if "glass" in labelstr:
        category = "Glass"
    elif "can" in labelstr or ("tin" in labelstr) or ("metal" in labelstr):
        category = "Can"
    elif "plastic" in labelstr or ("beer bottle" in labelstr):
        category = "Plastic"
    elif "box" in labelstr or ("cardboard" in labelstr) or ("paper" in labelstr):
        category = "Cardboard"
    elif "food" in labelL or ("Fruit" in labelL):
        category = "Compost"
    else:
        category = "Trash"
    
    post.category = category
    post.save()
    #recycle classify
    
    return render(request, 'detail.html',{'post':post, 'labelL':labelL, 'labels':labels, 'category':category, 'group':group })