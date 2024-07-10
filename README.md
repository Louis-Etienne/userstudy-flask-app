# User study Flask app

A Flask app for a user study where the user is asked to choose between two images. The images should be in the `/pic/background/` and `/pic/distorted/` folders.

First set up a virtual environment and install the required packages:
```
conda create -n user_study python
conda activate user_study
pip install -r requirements.txt
```

To run the app locally: 
```
python main.py
```

To deploy on Google Cloud App Engine:

1. Create a [MySQL database](https://cloud.google.com/sql/docs/mysql/create-instance) on Google Cloud SQL to store the results and fill-in the details in `main.py` and `app.yaml`.
2. Follow the tutorial [here](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) to deploy the flask app to Google Cloud.
