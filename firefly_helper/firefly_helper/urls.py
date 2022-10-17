"""firefly_helper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views import defaults as default_views
from main_app import views

admin.site.site_header = "Firefly Import Helpers"
admin.site.index_title = "Firefly Import Helpers"
admin.site.site_title = "Firefly Helper Backend"

urlpatterns = [
    path("console/doc/", include("django.contrib.admindocs.urls")),
    path("console/", admin.site.urls),
    path(
        "",
        views.index,
        name="index",
    ),
    path(
        "upload/<slug:category>/",
        views.upload_statements,
        name="upload_statements",
    ),
    path(
        "process/<slug:category>/<slug:file_ids>/",
        views.process_uploaded_files,
        name="process_uploaded_files",
    ),
    path(
        "processing/<slug:category>/<slug:file_ids>/",
        views.processing_uploaded_files,
        name="processing_uploaded_files",
    ),
    path(
        "cancel/<slug:category>/<slug:file_ids>/",
        views.cancel_uploaded_files,
        name="cancel_uploaded_files",
    ),
    path(
        "logs/<slug:category>/<slug:file_id>/", views.process_logs, name="process_logs"
    ),
    path(
        "faq/",
        views.faq_section,
        name="faq_section",
    ),
    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
