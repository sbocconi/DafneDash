from keycloak import KeycloakOpenID

from datadumps import read_yaml

class DafneKeycloak:
    # Get a token from Keycloak
    ## Configure client
    token = {}

    def __init__(self):
        pass
    
    @classmethod
    def read_token(cls):
        settings = read_yaml()['keycloak']
        keycloak_openid = KeycloakOpenID(server_url=settings['server_url'],
                                 client_id=settings['client_id'],
                                 realm_name=settings['realm'],
                                 client_secret_key=settings['client_secret'],
                                 verify=False
                                 )

        cls.token = keycloak_openid.token(settings['username'], settings['password'], scope="openid")
        breakpoint()
        print(f"Token received from Keycloak:\n {cls.token['access_token']}\n\n")

