""" run tests for pagetree

$ virtualenv ve
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
            'django_nose',
            'django_markwhat',
            'django_jenkins',
            'quizblock'
        ),
        TEST_RUNNER='django_nose.NoseTestSuiteRunner',
        MIDDLEWARE_CLASSES=[],
        NOSE_ARGS = [
            '--cover-package=quizblock',
        ],
        JENKINS_TASKS = (
            'django_jenkins.tasks.with_coverage',
        ),
        PROJECT_APPS = [
            'quizblock',
        ],
        COVERAGE_EXCLUDES_FOLDERS = ['migrations', 'south_migrations'],
        ROOT_URLCONF = [],
        PAGEBLOCKS = ['pagetree.TestBlock', 'quizblock.Quiz'],
        SOUTH_TESTS_MIGRATE=False,

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
    django.setup()
    # Fire off the tests
    call_command('jenkins')

if __name__ == '__main__':
    main()
