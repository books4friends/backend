import json
import os

from django import template
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.templatetags.staticfiles import static


register = template.Library()


FILE_NAME = '../webpack-stats.json'


def _get_bundle_file():
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), FILE_NAME)
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


@register.simple_tag
def load_bundle():
    bundle = _get_bundle_file()
    tags = []
    for chunk in bundle['chunks']['app']:
        if chunk['name'].endswith('.js'):
            tags.append(
                '<script type="text/javascript" src="{}"></script>'.format(static('frontend/app/' + chunk['name']))
            )
        elif chunk['name'].endswith('.css'):
            tags.append(
                '<link type="text/css" href="{}" rel="stylesheet"/>'.format(static('frontend/app/' + chunk['name']))
            )
    return mark_safe("\n".join(tags))
