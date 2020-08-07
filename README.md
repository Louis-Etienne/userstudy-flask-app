# User study Flask app

A Flask app for a user study where the user is asked to choose between two images. The images should be in the `/pic/background/` and `/pic/distorted/` folders. The app can be deployed to Google Cloud App Engine with:

```
 pip install -r requirements.txt -t lib/
 gcloud init
 gcloud app deploy
```

