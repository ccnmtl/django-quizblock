""" run tests for pagetree

$ virtualenv ve
$ ./ve/bin/pip install Django==4.2.11
$ ./ve/bin/pip install -r test_reqs.txt
$ ./ve/bin/python runtests.py
"""
from django.conf import settings
from django.core.management import call_command
import django


def main():
    # Dynamically configure the Django settings with the minimum necessary to
    # get Django running tests
    settings.configure(
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'pagetree',
            'quizblock'
        ),
        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [
                    # insert your TEMPLATE_DIRS here
                ],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.template.context_processors.debug',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.static',
                        'django.template.context_processors.tz',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],
        TEST_RUNNER='django.test.runner.DiscoverRunner',
        MIDDLEWARE=[],
        PROJECT_APPS = [
            'quizblock',
        ],
        COVERAGE_EXCLUDES_FOLDERS = ['migrations', 'south_migrations'],
        ROOT_URLCONF = [],
        PAGEBLOCKS = ['pagetree.TestBlock', 'quizblock.Quiz'],
        SOUTH_TESTS_MIGRATE=False,

        DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField',

        # Django replaces this, but it still wants it. *shrugs*
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
                'HOST': '',
                'PORT': '',
                'USER': '',
                'PASSWORD': '',
                }
            }
    )
    try:
        django.setup()
    except AttributeError:
        pass

    # Fire off the tests
    call_command('test')

if __name__ == '__main__':
    main()
