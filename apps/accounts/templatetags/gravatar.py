# apps/accounts/templatetags/gravatar.py
import hashlib
from django import template

register = template.Library()

@register.filter(name='gravatar_url')
def gravatar_url(email, size=100):
    """
    Return the Gravatar URL for the given email address.
    Usage in template: {{ user.email|gravatar_url:40 }}
    """
    if not email:
        return ''
    email_clean = email.strip().lower().encode('utf-8')
    email_hash = hashlib.md5(email_clean).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?d=mp&s={size}"

