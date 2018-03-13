from django.conf import settings


# export `HEROKU_APP_NAME` variable from settings for review app purposes
def heroku_app_name_var(request):
    return {'HEROKU_APP_NAME': settings.HEROKU_APP_NAME}
