# User study Flask app

A Flask app for a user study where the user is asked to choose between two images, one of the image is the Ground Truth and the other is a random matching image of a lighting technique. 
The images should be in their respective lighting technique folder in the `IMAGE_FOLDER_NAME` folder.

## Customize
1. Depending on your needs, you should change the constant variables : `HOST_NAME`,   `IMAGE_FOLDER_NAME`, `GT_FOLDER`, `NUMBER_IMAGES_PER_TECHNIQUE` in the `main.py` :
   - `HOST_NAME` : IP address of your output MySQL databse
   - `IMAGE_FOLDER_NAME` : path to your folder of images relative to the root of the project
   - `GT_FOLDER` : name of the ground truth folder inside the `IMAGE_FOLDER_NAME`
   - `NUMBER_IMAGES_PER_TECHNIQUE` : number of images presented to the user for each technique -> so the total amount of images presented to the user = number of technique * `NUMBER_IMAGES_PER_TECHNIQUE`

3. To get the user-study result, it is recommended to log the results to a MySQL databse, you can change the environment variables in the `app.yml` and the `HOST_NAME` in the `main.py` to log to your own databse
4. If you want to generate different combinations for the users doing the study you can change the `getRandomPairs` function in the `main.py`

## Deployment
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

Other way to deploy easily on Google Cloud App Engine : 

1. Activate the Cloud Shell : ![image](https://github.com/user-attachments/assets/33eab265-ccc7-486e-9c10-adb0fd1877bd)
2. In the Cloud Shell, clone this repo with a git command : `git clone https://github.com/Louis-Etienne/userstudy-flask-app.git`
3. Go inside the cloned repo : `cd userstudy-flask-app`
4. Deploy the app with this command : `gcloud app deploy`
5. Wait for the deployment! Then you can use the URL provided to reach your website!


## Special thanks!
Thanks dompm for the original repo!
