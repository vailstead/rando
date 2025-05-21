## Install
```
python3 -m venv env
source env/bin/activate
pip install django djangorestframework
django-admin startproject config .
python manage.py startapp api
```

## Settings
```
INSTALLED_APPS = [
    ...
    'rest_framework',
    'api',
]
```

## API
```
# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})
```

```
# api/urls.py
from django.urls import path
from .views import hello_world

urlpatterns = [
    path('hello/', hello_world),
]
```

```
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
```

## Run server
```
python manage.py migrate
python manage.py runserver
```

## Test Endpoint
```
curl http://127.0.0.1:8000/api/hello/
```

## More: View to upload csv
```
# api/views.py
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_csv(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    if not file_obj.name.endswith('.csv'):
        return Response({"error": "Only .csv files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, file_obj.name)

    with open(temp_file_path, 'wb+') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    return Response({
        "message": "File uploaded successfully",
        "temp_path": temp_file_path
    }, status=status.HTTP_201_CREATED)
```

```
# api/urls.py
from django.urls import path
from .views import hello_world, upload_csv

urlpatterns = [
    path('hello/', hello_world),
    path('upload-csv/', upload_csv),
]

```

Curl test
```
curl -X POST -F 'file=@example.csv' http://127.0.0.1:8000/api/upload-csv/
```

