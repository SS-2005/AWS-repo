# Dog Identification Project

## Overview
This project focuses on dog identification using Deep Learning techniques. It utilizes image processing and machine learning to classify dog breeds based on input images.


## Features
* Image Preprocessing: Load and preprocess dog images for model training.
* Model Training: Pre-trained model for classification.
* Prediction & Evaluation: Identify dog breeds and evaluate model performance.
* Multi-classification: Can accurately identify upto 120 breed of dogs.

## Dataset: 
I have used kaggle datset called `Dog Vision`<br>
dataset Link: `https://drive.google.com/file/d/1-0g9gvI7WjC_rmW4sSgQmSnPqSVlR72r/view?usp=drive_link`


## Usage and Working:

Colab Link `https://colab.research.google.com/drive/1zITjPOg-GC1rUEhlAtIH2MkxuET0gRXg?usp=drive_link`

1. Upload dataset in your drive and mount it.
2. Connect to GPU and Run the Jupyter Notebook and execute the cells step-by-step.
3. Upload a dog image for identification.
4. The model predicts the breed and displays the result.

## Challenges:

The requirment to train the model on image is itself a big challenge. 
* Understanding the dataset
* Features and properties of dataset
* Converting image to tensors(Making data read for machine to understand)
* As the dataset is quite long we cant afford to train it entirely on full dataset without checking everything and every parameter is right.
* Processing time of training
* Time taken for complete execution
* Evaluation parameters 


## Improvement:

The desired output is achieved in the current version however the performance can be more increased by the following.
* Using TPU
* Using GridSearchCV and finding best hyper-parameters for more accurate answers
* Imporving the dataset (Input data i.e image for this project)
* Feature extraction (Using relevant data only)
* Using some other method i.e modal selection 
* Using some better approch of transfer learning.

## Author:
Sahil Shaikh

