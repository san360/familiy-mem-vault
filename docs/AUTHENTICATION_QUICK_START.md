# Authentication Quick Start Guide

This is a condensed guide for implementing authentication in the Family Memory Vault app. For comprehensive details, see [AUTHENTICATION_RESEARCH.md](./AUTHENTICATION_RESEARCH.md).

## Recommended Solution: Azure AD B2C

**Why?** Native Azure integration, free tier (50K MAU), social logins, enterprise security, low maintenance.

---

## Quick Implementation Checklist

### ☁️ Azure Setup (2-3 days)

1. **Create Azure AD B2C Tenant**
   ```bash
   # Via Azure Portal
   - Go to portal.azure.com
   - Create new resource > Azure AD B2C
   - Create new tenant
   ```

2. **Register Applications**
   - Register SPA app (React frontend)
   - Register Web API app (FastAPI backend)
   - Note: Client IDs, Tenant ID, Tenant name

3. **Configure User Flows**
   - Sign up and sign in (B2C_1_SIGNUPSIGNIN)
   - Profile editing (B2C_1_PROFILEEDIT)
   - Password reset (B2C_1_PASSWORDRESET)

4. **Enable Social Providers**
   - Google
   - Microsoft
   - Apple (optional)

5. **Set Reply URLs**
   - Local: `http://localhost:5173`
   - Production: Your Azure Container Apps URL

---

### 🎨 Frontend Integration (3-5 days)

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install @azure/msal-browser @azure/msal-react
   ```

2. **Create Auth Config** (`src/authConfig.js`)
   ```javascript
   export const msalConfig = {
       auth: {
           clientId: "YOUR_CLIENT_ID",
           authority: "https://YOUR_TENANT.b2clogin.com/YOUR_TENANT.onmicrosoft.com/B2C_1_SIGNUPSIGNIN",
           knownAuthorities: ["YOUR_TENANT.b2clogin.com"],
           redirectUri: window.location.origin,
       },
       cache: {
           cacheLocation: "sessionStorage",
           storeAuthStateInCookie: false,
       }
   };
   
   export const loginRequest = {
       scopes: ["openid", "profile"]
   };
   ```

3. **Wrap App with Provider** (`src/main.jsx`)
   ```javascript
   import { MsalProvider } from "@azure/msal-react";
   import { PublicClientApplication } from "@azure/msal-browser";
   import { msalConfig } from "./authConfig";
   
   const msalInstance = new PublicClientApplication(msalConfig);
   
   ReactDOM.createRoot(document.getElementById('root')).render(
       <MsalProvider instance={msalInstance}>
           <App />
       </MsalProvider>
   );
   ```

4. **Create Auth Components**
   - `LoginButton.jsx` - Triggers sign-in
   - `LogoutButton.jsx` - Signs user out
   - `ProtectedRoute.jsx` - Wraps protected pages
   - `useAuth.js` - Custom hook for auth state

5. **Update API Calls**
   ```javascript
   // Get access token and add to headers
   const { instance, accounts } = useMsal();
   const accessToken = await instance.acquireTokenSilent({
       scopes: ["openid", "profile"],
       account: accounts[0]
   });
   
   // Add to API requests
   headers: {
       'Authorization': `Bearer ${accessToken.accessToken}`
   }
   ```

---

### 🔧 Backend Integration (2-3 days)

1. **Install Dependencies**
   ```bash
   cd backend
   pip install fastapi-azure-auth
   ```

2. **Update `requirements.txt`**
   ```
   fastapi-azure-auth==4.3.0
   ```

3. **Create Auth Module** (`backend/auth.py`)
   ```python
   from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
   
   azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
       app_client_id="YOUR_API_CLIENT_ID",
       tenant_id="YOUR_TENANT_ID",
       scopes={
           "api://YOUR_API_CLIENT_ID/user_impersonation": "Access API as user"
       }
   )
   
   # Initialize on startup using lifespan
   from contextlib import asynccontextmanager
   
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       await azure_scheme.openid_config.load_config()
       yield
   
   app = FastAPI(lifespan=lifespan)
   ```

4. **Protect Endpoints** (`backend/main.py`)
   ```python
   from fastapi import Depends, Security
   from auth import azure_scheme
   
   # Protected endpoint
   @app.get("/api/memories", dependencies=[Depends(azure_scheme)])
   async def get_memories():
       return {"memories": memories}
   
   # Get user info
   @app.get("/api/user/profile")
   async def get_user_profile(user = Security(azure_scheme)):
       return {
           "name": user.claims.get("name"),
           "email": user.claims.get("email"),
           "id": user.claims.get("sub")
       }
   ```

---

### 🧪 Testing (2-3 days)

1. **Local Testing**
   ```bash
   # Start backend
   cd backend
   python main.py
   
   # Start frontend
   cd frontend
   npm run dev
   ```

2. **Test Flows**
   - [ ] Sign up with email
   - [ ] Sign in with email
   - [ ] Sign in with Google
   - [ ] Sign in with Microsoft
   - [ ] Access protected route
   - [ ] API call with auth
   - [ ] Logout
   - [ ] Token refresh
   - [ ] Error handling

3. **Production Testing**
   - Deploy to Azure
   - Test with production URLs
   - Verify CORS settings
   - Check token validation

---

## Alternative: Simple JWT Auth

If Azure AD B2C is too complex, here's a simpler JWT approach:

### Backend
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate user credentials (check database)
    # If valid, create token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
        return username
    except JWTError:
        raise HTTPException(status_code=401)

@app.get("/api/memories")
async def get_memories(current_user: str = Depends(get_current_user)):
    return {"memories": memories, "user": current_user}
```

### Frontend
```javascript
// Login
const response = await fetch('http://localhost:8000/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
        username: 'user@example.com',
        password: 'password123'
    })
});
const { access_token } = await response.json();
localStorage.setItem('access_token', access_token);

// API calls
const token = localStorage.getItem('access_token');
fetch('http://localhost:8000/api/memories', {
    headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## Security Checklist

- [ ] Use HTTPS everywhere (production)
- [ ] Store tokens securely (httpOnly cookies or sessionStorage)
- [ ] Implement token expiration (15-30 minutes)
- [ ] Add refresh token mechanism
- [ ] Rate limit authentication endpoints
- [ ] Enable CORS with specific origins
- [ ] Add logging for auth events
- [ ] Implement logout on all devices
- [ ] Add MFA (optional but recommended)
- [ ] Regular security audits

---

## Troubleshooting

### Common Issues

**CORS errors:**
- Add frontend URL to backend CORS origins
- Add backend URL to Azure AD B2C reply URLs

**Token validation fails:**
- Check client IDs match
- Verify tenant ID is correct
- Ensure scopes are configured properly

**Redirect loop:**
- Check reply URLs in Azure portal
- Verify authority URL format

**Social login doesn't work:**
- Enable identity provider in Azure portal
- Configure provider credentials
- Test provider connection

---

## Resources

- [Full Research Document](./AUTHENTICATION_RESEARCH.md)
- [Azure AD B2C Docs](https://learn.microsoft.com/en-us/azure/active-directory-b2c/)
- [MSAL React](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react)
- [FastAPI Azure Auth](https://intility.github.io/fastapi-azure-auth/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

## Timeline Summary

| Phase | Duration | Tasks |
|-------|----------|-------|
| Azure Setup | 2-3 days | Create tenant, register apps, configure flows |
| Frontend | 3-5 days | Install packages, implement auth, test |
| Backend | 2-3 days | Install packages, protect endpoints, test |
| Testing | 2-3 days | E2E testing, deployment, validation |
| **Total** | **2-3 weeks** | Complete authentication implementation |

---

**Next Steps:** Choose your approach and start with Azure setup!
