import re
from django.conf import settings


def urlize_title(title):
    return re.sub(r'\s+', '_', title)

def deurlize_title(title):
    return re.sub(r'[_\s]+', ' ', title)

