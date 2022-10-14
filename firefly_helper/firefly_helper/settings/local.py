from .base import *  # noqa

import environ


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)

environ.Env.read_env(os.path.join(BASE_DIR, '.local.env'))



DEBUG = env('DEBUG')

TIME_ZONE = env("TIME_ZONE")


SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="28!9gv&n$-2+ze8!3dya+itl#nfkla@z41+pox!9u5##qpjm",
)


ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa F405


INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

INSTALLED_APPS += ["django_extensions"]  # noqa F405
CELERY_TASK_EAGER_PROPAGATES = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("POSTGRES_DB"),
        'USER': env("POSTGRES_USER"),
        'PASSWORD': env("POSTGRES_PASSWORD"),
        'HOST': env("POSTGRES_HOST"),
        'PORT': env("POSTGRES_PORT"),
    }
}

CELERY_BROKER_URL = env.cache('REDIS_URL')