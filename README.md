# Vue&Django

Use Django in the back end and Vue in the Front end of your aplication. vue_django creates a deictionary with base variables and an map of your API (using django-rest-framework), and pass all that information to a Vue application  so both frameworks can communicate more efficiently. 

## Instalation

1. Download this repo

2. Add vue_django to your aplications in your **settings.py**, it needs to be after  Django Rest Framework, and before your apps.

   **setings.py**

   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'rest_framework',
       'vue_django'
   ]
   ```

3. Create your API route,  should be a centralized route where you serve the en points of your api, it is useful to create a separated urls file to your api, such as api.py and add your endpoints to it, and then add it to your main urls file.

   **api.py**

   ```python
   urlpatterns = [
       url('accounts/',
           include(('myapp.accounts.urls','accounts'))
       ),    
       url('invoices/',
           include(('myapp.invoices.urls','invoices'))
       ),
   ]
   ```

    **urls.py**