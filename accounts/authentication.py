# authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.core.cache import cache

class BlacklistJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        
        user, token = result
        
        
        jti = token.get('jti')  
        if cache.get(f"blacklist_{jti}"):
            raise InvalidToken("Token has been blacklisted.")
        
        return user, token
    
    