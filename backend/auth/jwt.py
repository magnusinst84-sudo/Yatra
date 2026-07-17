import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def init_firebase():
    if not firebase_admin._apps:
        try:
            firebase_config_str = os.environ.get("FIREBASE_ADMIN_SDK_JSON")
            if firebase_config_str:
                # Try to parse as JSON string
                try:
                    cred_dict = json.loads(firebase_config_str)
                    cred = credentials.Certificate(cred_dict)
                except json.JSONDecodeError:
                    # Maybe it's a file path
                    if os.path.exists(firebase_config_str):
                        cred = credentials.Certificate(firebase_config_str)
                    else:
                        print("Warning: FIREBASE_ADMIN_SDK_JSON is neither valid JSON nor a valid file path.")
                        return
                
                firebase_admin.initialize_app(cred)
            else:
                print("Warning: FIREBASE_ADMIN_SDK_JSON environment variable not set.")
        except Exception as e:
            print(f"Failed to initialize Firebase Admin: {e}")

# Initialize on module load
init_firebase()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    FastAPI Dependency to verify Firebase ID tokens.
    Usage in routes: user = Depends(get_current_user)
    """
    if not firebase_admin._apps:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase Admin SDK is not initialized properly"
        )
    
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}"
        )
