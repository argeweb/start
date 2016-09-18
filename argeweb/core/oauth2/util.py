import httplib2


def credentials_to_token(credentials):
    """
    Transforms an Oauth2 credentials object into an OAuth2Token object
    to be used with the legacy gdata API
    """
    import gdata.gauth

    credentials.refresh(httplib2.Http())
    token = gdata.gauth.OAuth2Token(
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        scope=credentials.scope,
        user_agent='Google App Engine / argeweb Framework',
        access_token=credentials.access_token,
        refresh_token=credentials.refresh_token)
    return token
